<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
<h2>Running Instances Summary</h2>

<table border="0" style="empty-cells:show;" width="100%">
<tr>
<td>    
<h3>Master Account (joe@example.com)</h3>
<table border="1" style="empty-cells:show;">
<xsl:variable name="acct" select="'joe@example.com'"/>
  <tr>
    <td>Windows Large</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$acct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.large' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Windows Small</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$acct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.small' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Windows Micro</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$acct]/Region/EC2/Instance/EC2-Instance[instance_type='t1.micro' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Large</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$acct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.large' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Small</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$acct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.small' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Micro</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$acct]/Region/EC2/Instance/EC2-Instance[instance_type='t1.micro' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td><b>Total</b></td>
    <td><b><xsl:value-of select="count(Audit/Account[@name=$acct]/Region/EC2/Instance/EC2-Instance[state='running'])"/></b></td>
  </tr>
</table>
</td>

<td>
<h3>Production Account (joep@example.com)</h3>
<table border="1" style="empty-cells:show;">
<xsl:variable name="pacct" select="'joep@example.com'"/>
  <tr>
    <td>Windows Large</td>
    <td><xsl:value-of select="count(/Audit/Account[@name=$pacct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.large' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Windows Small</td>
    <td><xsl:value-of select="count(/Audit/Account[@name=$pacct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.small' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Windows Micro</td>
    <td><xsl:value-of select="count(/Audit/Account[@name=$pacct]/Region/EC2/Instance/EC2-Instance[instance_type='t1.micro' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Large</td>
    <td><xsl:value-of select="count(/Audit/Account[@name=$pacct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.large' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Small</td>
    <td><xsl:value-of select="count(/Audit/Account[@name=$pacct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.small' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Micro</td>
    <td><xsl:value-of select="count(/Audit/Account[@name=$pacct]/Region/EC2/Instance/EC2-Instance[instance_type='t1.micro' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td><b>Total</b></td>
    <td><b><xsl:value-of select="count(/Audit/Account[@name=$pacct]/Region/EC2/Instance/EC2-Instance[state='running'])"/></b></td>
  </tr>
</table>
</td>

<td>
<h3>Development Account (joed@example.com)</h3>
<table border="1" style="empty-cells:show;">
<xsl:variable name="dacct" select="'joed@example.com'"/>
  <tr>
    <td>Windows Large</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$dacct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.large' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Windows Small</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$dacct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.small' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Windows Micro</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$dacct]/Region/EC2/Instance/EC2-Instance[instance_type='t1.micro' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Large</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$dacct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.large' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Small</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$dacct]/Region/EC2/Instance/EC2-Instance[instance_type='m1.small' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Micro</td>
    <td><xsl:value-of select="count(Audit/Account[@name=$dacct]/Region/EC2/Instance/EC2-Instance[instance_type='t1.micro' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td><b>Total</b></td>
    <td><b><xsl:value-of select="count(Audit/Account[@name=$dacct]/Region/EC2/Instance/EC2-Instance[state='running'])"/></b></td>
  </tr>
</table>
</td>
</tr>
</table>

<h3>All Accounts</h3>
<table border="1" style="empty-cells:show;">
  <tr>
    <td>Windows Large</td>
    <td><xsl:value-of select="count(Audit/Account/Region/EC2/Instance/EC2-Instance[instance_type='m1.large' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Windows Small</td>
    <td><xsl:value-of select="count(Audit/Account/Region/EC2/Instance/EC2-Instance[instance_type='m1.small' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Windows Micro</td>
    <td><xsl:value-of select="count(Audit/Account/Region/EC2/Instance/EC2-Instance[instance_type='t1.micro' and state='running' and virtualizationType='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Large</td>
    <td><xsl:value-of select="count(Audit/Account/Region/EC2/Instance/EC2-Instance[instance_type='m1.large' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Small</td>
    <td><xsl:value-of select="count(Audit/Account/Region/EC2/Instance/EC2-Instance[instance_type='m1.small' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td>Non-windows Micro</td>
    <td><xsl:value-of select="count(Audit/Account/Region/EC2/Instance/EC2-Instance[instance_type='t1.micro' and state='running' and virtualizationType!='hvm'])"/></td>
  </tr>
  <tr>
    <td><b>Total</b></td>
    <td><b><xsl:value-of select="count(Audit/Account/Region/EC2/Instance/EC2-Instance[state='running'])"/></b></td>
  </tr>
</table>

<br/>
</xsl:template>

</xsl:stylesheet>

