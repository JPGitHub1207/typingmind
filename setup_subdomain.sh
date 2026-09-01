#!/bin/bash

# Subdomain Setup Script for fe.learningtalent.co.uk
# Run this script in Azure Cloud Shell

echo "=== Setting up subdomain: fe.learningtalent.co.uk ==="

# Set variables
RESOURCE_GROUP="dns-zone-rg"
ZONE_NAME="learningtalent.co.uk"
SUBDOMAIN="fe"

echo "Step 1: Creating DNS records..."

# Create TXT record for verification
echo "Creating TXT record for domain verification..."
az network dns record-set txt create \
  --resource-group "$RESOURCE_GROUP" \
  --zone-name "$ZONE_NAME" \
  --name "$SUBDOMAIN" \
  --ttl 300

az network dns record-set txt add-record \
  --resource-group "$RESOURCE_GROUP" \
  --zone-name "$ZONE_NAME" \
  --record-set-name "$SUBDOMAIN" \
  --value "MS=VERIFY_FE"

echo "TXT record created successfully!"

# Create MX record for email
echo "Creating MX record for email..."
az network dns record-set mx create \
  --resource-group "$RESOURCE_GROUP" \
  --zone-name "$ZONE_NAME" \
  --name "$SUBDOMAIN" \
  --ttl 300

az network dns record-set mx add-record \
  --resource-group "$RESOURCE_GROUP" \
  --zone-name "$ZONE_NAME" \
  --record-set-name "$SUBDOMAIN" \
  --exchange "0 fe-learningtalent-co-uk.mail.protection.outlook.com" \
  --preference 0

echo "MX record created successfully!"

# Create CNAME for autodiscover
echo "Creating CNAME record for autodiscover..."
az network dns record-set cname create \
  --resource-group "$RESOURCE_GROUP" \
  --zone-name "$ZONE_NAME" \
  --name "autodiscover.$SUBDOMAIN" \
  --ttl 300

az network dns record-set cname set-record \
  --resource-group "$RESOURCE_GROUP" \
  --zone-name "$ZONE_NAME" \
  --record-set-name "autodiscover.$SUBDOMAIN" \
  --cname "autodiscover.outlook.com"

echo "CNAME record created successfully!"

echo "Step 2: Verifying DNS propagation..."
echo "Waiting 30 seconds for DNS propagation..."
sleep 30

# Check DNS records
echo "Checking TXT record..."
nslookup -type=TXT fe.learningtalent.co.uk

echo "Checking MX record..."
nslookup -type=MX fe.learningtalent.co.uk

echo "Checking CNAME record..."
nslookup -type=CNAME autodiscover.fe.learningtalent.co.uk

echo "Step 3: DNS setup complete!"
echo "Next steps:"
echo "1. Go to Microsoft 365 admin center"
echo "2. Navigate to Settings → Domains"
echo "3. Click '+ Add domain'"
echo "4. Enter: fe.learningtalent.co.uk"
echo "5. Click 'Add domain' and then 'Verify'"

echo "=== Script completed ==="