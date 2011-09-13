<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
<h2>Amazon RDS (DB) Instances</h2>
<table border="1" style="empty-cells:show;" width="100%">
  <tr bgcolor="lightgrey">
    <th>Account</th>
    <th>ID</th>
    <th>Type</th>
    <th>Engine</th>
    <th>Endpoint</th>
    <th>Security Group</th>
    <th>Multi-AZ</th>
    <th>Master User</th>
    <th>Storage (GB)</th>
  </tr>
  <xsl:for-each select="Audit/Account/Region/RDS/Instances/instance">
  <tr>
    <xsl:variable name="accountName" select="../../../../@name"/>
    <xsl:variable name="awsAccount" select="../../../../@awsNumber"/>
    <xsl:variable name="iamLink" select="concat(concat('https://',$awsAccount), '.signin.aws.amazon.com/console')"/>
    <xsl:variable name="accountNameProcess" select="'@example.com'"/>
    <xsl:variable name="accountNameShort" select="substring-before($accountName,$accountNameProcess)"/>
    <td><a><xsl:attribute name="href"><xsl:value-of select="$iamLink"/></xsl:attribute><xsl:attribute name="target">_blank</xsl:attribute><xsl:value-of select="$accountNameShort"/></a></td>
    <td><xsl:value-of select="id"/></td>
    <td><xsl:value-of select="instance_class"/></td>
    <td><xsl:value-of select="engine"/></td>
    <td><xsl:value-of select="_address"/></td>
    <td><xsl:value-of select="security_group"/></td>
    <td><xsl:value-of select="multi_az"/></td>
    <td><xsl:value-of select="master_username"/></td>
    <td><xsl:value-of select="allocated_storage"/></td>

  </tr>
  </xsl:for-each>
</table><br/>
<br/>
</xsl:template>

</xsl:stylesheet>

