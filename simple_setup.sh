#!/bin/bash
echo "=== Setting up subdomain: fe.learningtalent.co.uk ==="

# Create TXT record
az network dns record-set txt create --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --name "fe" --ttl 300
az network dns record-set txt add-record --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --record-set-name "fe" --value "MS=VERIFY_FE"

# Create MX record
az network dns record-set mx create --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --name "fe" --ttl 300
az network dns record-set mx add-record --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --record-set-name "fe" --exchange "0 fe-learningtalent-co-uk.mail.protection.outlook.com" --preference 0

# Create CNAME record
az network dns record-set cname create --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --name "autodiscover.fe" --ttl 300
az network dns record-set cname set-record --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --record-set-name "autodiscover.fe" --cname "autodiscover.outlook.com"

echo "DNS records created! Now verify in Microsoft 365 admin center."