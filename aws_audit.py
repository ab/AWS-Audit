#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

'''
aws_audit.py - Queries a bunch of AWS accounts and produce an XML document from the details
returned by the Amazon API. What you use the resulting XML file is entirely up to you. :)
Any number of accounts can be queried, and it will look in every AWS region.

It is massively rough around the edges! Please feel free to improve!

It uses a configuration file in /etc/aws_audit.conf by default. You can specify
a different location with the first argument on the command-line.

This configuration file will require a 'master' AWS API key and secret, this AWS account
should have access to an S3 bucket containing the credentials of any other AWS accounts
that you would like to be included in the output. Please read the README.

'''
import os
import re
import shutil
import sys
import time
import urllib
import yaml
import xml.etree.cElementTree as ET

from types import *

import boto
import boto.ec2
import boto.rds
import boto.sdb

if len(sys.argv) >= 2:
    config_file = sys.argv[1]
else:
    config_file = '/etc/aws_audit.conf'

try:
    config = yaml.safe_load(open(config_file, 'r'))
except IOError, err:
    print 'Failed to open config file.'
    print err
    print ''
    print 'usage: ' + os.path.basename(sys.argv[0]) + ' CONFIG'
    sys.exit(2)

primaryregion = config['primary_region']
subaccounts = []

print "Auditing our AWS usage and building XML data file."
print "CAUTION: This is a long process, and can take up to"
print "ten minutes to complete. Do not cancel once started."

print "Connecting to the master S3 bucket containing our keys"
master_s3 = boto.connect_s3(aws_access_key_id=config['master_aws_key'], aws_secret_access_key=config['master_aws_secret'])
master_bucket = master_s3.get_bucket(config['credential_bucket'])
keys = master_bucket.get_all_keys()
regex = re.compile('.*\/cred\-.*\.txt$')
print "Extracting keys"
for key in keys:
    if regex.match(key.name):
        filename = key.name.split('/')[1]
        file_contents = key.get_contents_as_string()
        lines = file_contents.split('\n')
        for line in lines:
            line = line.replace('\r', '')
            cols = line.split('=')
            if cols[0] == "AccountName":
                aws_account = cols[1]
                print "Found keys for account: "+aws_account
            if cols[0] == "AWSAccessKeyId":
                aws_key = cols[1]
            if cols[0] == "AWSSecretKey":
                aws_secret = cols[1]
        found_creds = {"aws_account":aws_account, "aws_key":aws_key, "aws_secret":aws_secret}
        subaccounts.append(found_creds)

print "Building XML document. This will take some time."
xml_root = ET.Element('Audit')
comment = ET.Comment(config['xml_comment'])
xml_root.append(comment)
xml_codeinfo = ET.SubElement(xml_root,'CodeInfo')
xml_generator = ET.SubElement(xml_codeinfo,'Generator')
xml_generator.attrib['version'] = '0.5'
xml_generator.attrib['application'] = 'aws_audit.py'

xml_revhistory = ET.SubElement(xml_codeinfo,'Contact')
xml_revhistory.attrib['name'] = config['xml_contact_name']
xml_revhistory.attrib['email'] = config['xml_contact_email']

def get_account_id(access_key_id, secret_access_key):
    """Parse the account number from IAM output for current user."""
    iam = boto.connect_iam(aws_access_key_id=access_key_id,
                           aws_secret_access_key=secret_access_key)
    response = iam.get_user()
    string = response['get_user_response']['get_user_result']['user']['arn']
    return string.split(':')[4]

for account in subaccounts:
    print "Building XML for account: "+account['aws_account']
    xml_acctdetails = ET.SubElement(xml_root,'Account')
    xml_acctdetails.attrib['name'] = account['aws_account']

    xml_acctdetails.attrib['awsNumber'] = get_account_id(account['aws_key'],
                                                         account['aws_secret'])

    regions = config['regions'].split(",")
    for region in regions:
        print "Looking in %s: " % (region)
        conn = boto.ec2.connect_to_region(region, aws_access_key_id=account['aws_key'], aws_secret_access_key=account['aws_secret'])

        xml_region = ET.SubElement(xml_acctdetails,'Region')
        xml_region.attrib['name'] = region
        xml_ec2 = ET.SubElement(xml_region,'EC2')
        xml_instance = ET.SubElement(xml_ec2,'Instance')
        print "Parsing EC2 data"
        try:
            reservations = conn.get_all_instances()
            instances = [i for r in reservations for i in r.instances]
            for i in instances:
                obj = i.__dict__
                xml_ec2instance = ET.SubElement(xml_instance,'EC2-Instance')
                for k, v in obj.items():
                    if "tags" in k:
                        xml_tagdata = ''
                        for a, b in v.items():
                        ## Fix For elasticmapreduce ##
                            if re.search(':',a):
                                a = a.replace(":","_")
                                ## Remove White Spaces ##
                            a = a.replace(' ','')
                            xml_tagdata = ET.SubElement(xml_ec2instance,a + "Tag")
                            xml_tagdata.text = b
                    if "block_device_mapping" in k:
                        xml_blockdevicedata = ET.SubElement(xml_ec2instance,"block_device_data")
                        for mount, volume in v.items():
                            xml_blockdevicemount = ET.SubElement(xml_blockdevicedata,"mount")
                            xml_blockdevicemount.text = mount
                            obj = volume.__dict__
                            for a, b in obj.items():
                                a = str(a)
                                b = str(b)
                                xml_blockdevicevolume = ET.SubElement(xml_blockdevicemount,a)
                                xml_blockdevicevolume.text = b
                    else:
                        v = str(v)
                        xml_instdata = ET.SubElement(xml_ec2instance,k)
                        xml_instdata.text = v
        except AttributeError:
           print "No data found for account %s and region %s" % (account_id, region)

        print "Parsing Security Groups"
        try:
            xml_securitygroups = ET.SubElement(xml_ec2,'SecurityGroups')
            securitygroups = conn.get_all_security_groups()
            for sg in securitygroups:
                xml_securitygroup = ET.SubElement(xml_securitygroups,'SecurityGroup')
                obj = sg.__dict__
                for k, v in obj.items():
                    # print "%s=%s" % (k, v)
                    if "name" in k:
                        xml_sgname = ET.SubElement(xml_securitygroup,k)
                        xml_sgname.text = v

                    if "rules" in k:
                        xml_sgrules = ET.SubElement(xml_securitygroup,'Rules')
                        for rule in v:
                            rule = str(rule)
                            xml_sgrule = ET.SubElement(xml_sgrules,'Rule')
                            xml_sgrule.text = rule
                    v = str(v)
                    xml_sgdata = ET.SubElement(xml_securitygroup,k)
                    xml_sgdata.text = v
        except AttributeError:
           print "No data found for account %s and region %s" % (account_id, region)

        print "Parsing Elastic IPs"
        try:
            xml_elasticips = ET.SubElement(xml_ec2,'ElasticIPs')
            addresses = conn.get_all_addresses()
            for address in addresses:
                xml_eipaddress = ET.SubElement(xml_elasticips,'Address')
                xml_eip_public = ET.SubElement(xml_eipaddress,'public_ip')
                xml_eip_public.text = address.public_ip
                xml_eip_instanceid = ET.SubElement(xml_eipaddress,'instance_id')
                xml_eip_instanceid.text = address.instance_id
                xml_eip_region = ET.SubElement(xml_eipaddress,'region')
                xml_eip_region.text = address.region.name
        except AttributeError:
           print "No data found for account %s and region %s" % (account_id, region)
        except boto.exception.EC2ResponseError, err:
           print "Error from API: %s" % (err)

        print "Parsing Volumes & Snapshots"
        try:
            xml_volumes = ET.SubElement(xml_ec2,'Volumes')
            volumes = conn.get_all_volumes()
            for vol in volumes:
                xml_volume = ET.SubElement(xml_volumes,'Volume')
                xml_volume_id = ET.SubElement(xml_volume,'id')
                xml_volume_id.text = vol.id
                if "Name" in vol.tags:
                    xml_volume_tag = ET.SubElement(xml_volume,'NameTag')
                    xml_volume_tag.text = vol.tags["Name"]
                else:
                    xml_volume_tag = ET.SubElement(xml_volume,'NameTag')
                    xml_volume_tag.text = '!!NO NAME!!'
                xml_volume_status = ET.SubElement(xml_volume,'status')
                xml_volume_status.text = str(vol.status)
                xml_volume_region = ET.SubElement(xml_volume,'region')
                xml_volume_region.text = str(vol.region)
                xml_volume_zone = ET.SubElement(xml_volume,'zone')
                xml_volume_zone.text = str(vol.zone)
                xml_volume_size = ET.SubElement(xml_volume,'sizeMB')
                xml_volume_size.text = str(vol.size)
                if hasattr(vol, 'attach_data'):
                    if type(vol.attach_data.instance_id) is not NoneType:
                        xml_volume_attach_id = ET.SubElement(xml_volume,'attachedToInstanceId')
                        xml_volume_attach_id.text = vol.attach_data.instance_id
                        xml_volume_attach_dev = ET.SubElement(xml_volume,'attachedToInstanceDev')
                        xml_volume_attach_dev.text = vol.attach_data.device
                        xml_volume_attach_del = ET.SubElement(xml_volume,'deleteOnTermination')
                        xml_volume_attach_del.text = vol.attach_data.deleteOnTermination
        except AttributeError:
           print "No data found for account %s and region %s" % (account_id, region)

        try:
            print "Parsing RDS data"
            xml_rds = ET.SubElement(xml_region,'RDS')
            rds_region = boto.rds.RDSRegionInfo(name=region, endpoint='rds.'+region+'.amazonaws.com')
            conn_rds = boto.rds.RDSConnection(aws_access_key_id=account['aws_key'], aws_secret_access_key=account['aws_secret'], region=rds_region)
            xml_rds_instances = ET.SubElement(xml_rds,'Instances')
            rds_instances = conn_rds.get_all_dbinstances()
            for instance in rds_instances:
                instance = instance.__dict__
                xml_rds_instance = ET.SubElement(xml_rds_instances,'instance')
                for k, v in instance.items():
                    xml_rds_data = ET.SubElement(xml_rds_instance,k)
                    xml_rds_data.text = str(v)
        except AttributeError:
           print "No data found for account %s and region %s" % (account_id, region)

        try:
            print "Parsing SimpleDB data"
            xml_sdb = ET.SubElement(xml_region,'SimpleDB')
            if region == 'us-east-1':
               sdb_region = boto.sdb.SDBRegionInfo(name=region, endpoint='sdb.amazonaws.com')
            else:
               sdb_region = boto.sdb.SDBRegionInfo(name=region, endpoint='sdb.'+region+'.amazonaws.com')
            conn_sdb = boto.sdb.connection.SDBConnection(aws_access_key_id=account['aws_key'], aws_secret_access_key=account['aws_secret'], region=sdb_region)
            xml_sdb_domains = ET.SubElement(xml_sdb,'Domains')
            sdb_domains = conn_sdb.get_all_domains()
            for domain in sdb_domains:
                domain = domain.__dict__
                xml_sdb_domain = ET.SubElement(xml_sdb_domains,'domain')
                for k, v in domain.items():
                    xml_sdb_data = ET.SubElement(xml_sdb_domain,k)
                    xml_sdb_data.text = str(v)
        except AttributeError, err:
           print "No data found for account %s and region %s (%s)" % (account_id, region, err)

        try:
            print "Parsing RDS Security Groups"
            xml_rds_sg = ET.SubElement(xml_rds,'SecurityGroups')
            rds_dbsg = conn_rds.get_all_dbsecurity_groups()
            for sg in rds_dbsg:
                xml_rds_sg_sg = ET.SubElement(xml_rds_sg,'SecurityGroup')
                xml_rds_sg_name = ET.SubElement(xml_rds_sg_sg,'name')
                xml_rds_sg_name.text = sg.name
                xml_rds_sg_owner = ET.SubElement(xml_rds_sg_sg,'owner_id')
                xml_rds_sg_owner.text = sg.owner_id
                xml_rds_sg_desc = ET.SubElement(xml_rds_sg_sg,'description')
                xml_rds_sg_desc.text = sg.description
                xml_rds_sg_access = ET.SubElement(xml_rds_sg_sg,'allow_access')
                for ec2 in sg.ec2_groups:
                    xml_rds_sg_access_group = ET.SubElement(xml_rds_sg_access,'ec2_security_groups')
                    xml_rds_sg_access_group = ec2.name
                for ip in sg.ip_ranges:
                    xml_rds_sg_access_cidr = ET.SubElement(xml_rds_sg_access,'cidr_ip')
                    xml_rds_sg_access_cidr.text = ip.cidr_ip
        except AttributeError:
            print "No data found for account %s and region %s" % (account_id, region)

    print "Parsing IAM data"
    try:
        xml_iam = ET.SubElement(xml_acctdetails,'IAM')
        conn_iam = boto.connect_iam(aws_access_key_id=account['aws_key'], aws_secret_access_key=account['aws_secret'])
        groups = conn_iam.get_all_groups()
        gresult = groups.ListGroupsResponse.ListGroupsResult
        if hasattr(gresult, 'Groups'):
            for group in gresult.Groups:
                xml_group = ET.SubElement(xml_iam,'group')
                for k, v in group.items():
                    xml_group_data = ET.SubElement(xml_group,k)
                    xml_group_data.text = v
                users = conn_iam.get_group(group.GroupName)
                uresult = users.GetGroupResponse.GetGroupResult
                if hasattr(uresult, 'Users'):
                    for user in uresult.Users:
                        xml_group_member = ET.SubElement(xml_group,'MemberUserName')
                        xml_group_member.text = user.UserName

                policies = conn_iam.get_all_group_policies(group.GroupName)
                presult = policies.ListGroupPoliciesResponse.ListGroupPoliciesResult
                if hasattr(presult, 'PolicyNames'):
                    for policy in presult.PolicyNames:
                        xml_group_policy = ET.SubElement(xml_group,'policy')
                        xml_group_policy_name = ET.SubElement(xml_group_policy,'name')
                        xml_group_policy_name.text = policy
                        gpolicy = conn_iam.get_group_policy(group.GroupName, policy)
                        xml_group_policy_doc = ET.SubElement(xml_group_policy,'PolicyDocument')
                        xml_group_policy_doc.text = urllib.unquote(gpolicy.GetGroupPolicyResponse.GetGroupPolicyResult.PolicyDocument)
            users = conn_iam.get_all_users()
            uresult = users.ListUsersResponse.ListUsersResult
            if hasattr (uresult, 'Users'):
                for user in uresult.Users:
                    xml_user = ET.SubElement(xml_iam,'User')

                    for k, v in user.items():
                        xml_user_data = ET.SubElement(xml_user,k)
                        xml_user_data.text = v

                memberof = conn_iam.get_groups_for_user(user.UserName)
                result = memberof.ListGroupsForUserResponse.ListGroupsForUserResult
                if hasattr (result, 'Groups'):
                    xml_user_groups = ET.SubElement(xml_user,'MemberOfGroup')
                    xml_user_groups.text = group.GroupName
                    policies = conn_iam.get_all_user_policies(user.UserName)
                    result = policies.ListUserPoliciesResponse.ListUserPoliciesResult
                    if hasattr (result, 'PolicyNames'):
                        for policy in result.PolicyNames:
                            xml_user_policies = ET.SubElement(xml_user,'PolicyNames')
                            xml_user_policy = ET.SubElement(xml_user_policies,'policy')
                            xml_user_policy_name = ET.SubElement(xml_user_policy,'name')
                            xml_user_policy_name.text = policy
                            upolicy = conn_iam.get_user_policy(user.UserName, policy)
                            xml_user_policy_name_doc = ET.SubElement(xml_user_policy,'PolicyDocument')
                            xml_user_policy_name_doc.text = urllib.unquote(upolicy.GetUserPolicyResponse.GetUserPolicyResult.PolicyDocument)
    except AttributeError:
        print "No data found for account %s and region %s" % (account_id, region)

    print "Parsing S3 bucket data"
    try:
        xml_s3 = ET.SubElement(xml_acctdetails,'S3')
        conn_s3 = boto.connect_s3(aws_access_key_id=account['aws_key'], aws_secret_access_key=account['aws_secret'])
        buckets = conn_s3.get_all_buckets()
        for bucket in buckets:
            xml_s3_bucket = ET.SubElement(xml_s3,'bucket')
            xml_s3_bucket_name = ET.SubElement(xml_s3_bucket,'name')
            xml_s3_bucket_name.text = bucket.name
            xml_s3_bucket_loc = ET.SubElement(xml_s3_bucket,'Location')
            xml_s3_bucket_loc.text = bucket.get_location()
            s3_acl = bucket.get_xml_acl().replace('<?xml version="1.0" encoding="UTF-8"?>\n', '')
            xml_s3_bucket_acl = ET.SubElement(xml_s3_bucket,'Policy')
            xml_s3_bucket_acl.text = s3_acl
    except AttributeError:
        print "No data found for account %s and region %s" % (account_id, region)

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
print "Reformatting XML"
indent(xml_root)

outputfile = config['output_file']
oldoutput = outputfile+'.old'
print "Backing up previous XML file"
shutil.copy(outputfile,oldoutput)

print "Writing new XML file"
file = open(outputfile,'w')
root = ET.ElementTree(xml_root)

root.write(file)
file.close()

print "Done"
