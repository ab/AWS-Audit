<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
<h2>Amazon VPC Instances</h2>
<table border="1" style="empty-cells:show;" width="100%">
  <tr bgcolor="lightgrey">
    <th>Account</th>
    <th>Name(T)</th>
    <th>ID</th>
    <th>Type</th>
    <th>Owner(T)</th>
    <th>Service(T)</th>
    <th>Notes(T)</th>
    <th>DNS Hostname(T)</th>
    <th>ContactEmail(T)</th>
    <th>ExpiryDate(T)</th>
    <th>Status</th>
    <th>Public IP</th>
    <th>Private IP</th>
  </tr>
  <xsl:for-each select="Audit/Account/Region/EC2/Instance/EC2-Instance">
  <xsl:if test="vpc_id != 'None'">
  <tr>
    <xsl:variable name="accountName" select="../../../../@name"/>
    <xsl:variable name="awsAccount" select="../../../../@awsNumber"/>
    <xsl:variable name="iamLink" select="concat(concat('https://',$awsAccount), '.signin.aws.amazon.com/console')"/>
    <xsl:variable name="accountNameProcess" select="'@example.com'"/>
    <xsl:variable name="accountNameShort" select="substring-before($accountName,$accountNameProcess)"/>
    <td><a><xsl:attribute name="href"><xsl:value-of select="$iamLink"/></xsl:attribute><xsl:attribute name="target">_blank</xsl:attribute><xsl:value-of select="$accountNameShort"/></a></td>
    <td><xsl:value-of select="NameTag"/></td>
    <td><xsl:value-of select="id"/></td>
    <xsl:choose>
      <xsl:when test="instance_type = 't1.micro'">
        <td bgcolor="#5CB3FF">m</td>
      </xsl:when>
      <xsl:when test="instance_type = 'm1.small'">
        <td bgcolor="#B041FF">S</td>
      </xsl:when>
      <xsl:when test="instance_type = 'm1.large'">
        <td bgcolor="#ADDFFF">L</td>
      </xsl:when>
      <xsl:when test="instance_type = 'c1.medium'">
        <td bgcolor="#00FFFF">M</td>
      </xsl:when>
      <xsl:otherwise>
        <td><xsl:value-of select="instance_type"/></td>
      </xsl:otherwise>
    </xsl:choose>
    <td><xsl:value-of select="OwnerTag"/></td>
    <td><xsl:value-of select="ServiceTag"/></td>
    <td><xsl:value-of select="NotesTag"/></td>
    <td><xsl:value-of select="HostnameTag"/></td>
    <td><xsl:value-of select="ContactEmailTag"/></td>
    <td><xsl:value-of select="ExpiryDateTag"/></td>
    <xsl:choose>
      <xsl:when test="state != 'running'">
        <td bgcolor="red"><xsl:value-of select="state"/></td>
      </xsl:when>
      <xsl:otherwise>
        <td><xsl:value-of select="state"/></td>
      </xsl:otherwise>
    </xsl:choose>
    <td><xsl:value-of select="ip_address"/></td>
    <td><xsl:value-of select="private_ip_address"/></td>

  </tr>
  </xsl:if>
  </xsl:for-each>
</table><br/>
<br/>
</xsl:template>

</xsl:stylesheet>

