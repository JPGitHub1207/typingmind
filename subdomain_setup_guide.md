# Subdomain Setup Guide for learningtalent.co.uk

## Current Status
- Primary domain: `learningtalent.co.uk` (Federated)
- Default domain: `NETORGFT18327802.onmicrosoft.com` (Managed)
- Target subdomain: `fe.learningtalent.co.uk`

## Step 1: DNS Setup in Azure

### 1.1 Create TXT Record for Verification
```bash
az network dns record-set txt create --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --name "fe" --ttl 300
az network dns record-set txt add-record --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --record-set-name "fe" --value "MS=VERIFY_FE"
```

### 1.2 Create MX Record for Email
```bash
az network dns record-set mx create --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --name "fe" --ttl 300
az network dns record-set mx add-record --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --record-set-name "fe" --exchange "0 fe-learningtalent-co-uk.mail.protection.outlook.com" --preference 0
```

### 1.3 Create CNAME for Autodiscover
```bash
az network dns record-set cname create --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --name "autodiscover.fe" --ttl 300
az network dns record-set cname set-record --resource-group "dns-zone-rg" --zone-name "learningtalent.co.uk" --record-set-name "autodiscover.fe" --cname "autodiscover.outlook.com"
```

## Step 2: Verify DNS Propagation
```bash
# Check TXT record
nslookup -type=TXT fe.learningtalent.co.uk

# Check MX record
nslookup -type=MX fe.learningtalent.co.uk

# Check CNAME record
nslookup -type=CNAME autodiscover.fe.learningtalent.co.uk
```

## Step 3: Add Domain to Microsoft 365

### 3.1 Via Microsoft 365 Admin Center
1. Go to https://admin.microsoft.com
2. Navigate to Settings → Domains
3. Click "+ Add domain"
4. Enter: `fe.learningtalent.co.uk`
5. Click "Add domain"
6. Click "Verify"

### 3.2 Via PowerShell (Alternative)
```powershell
# Connect to Microsoft Graph
Connect-MgGraph -Scopes "Directory.ReadWrite.All"

# Add domain
$body = @{ id = "fe.learningtalent.co.uk" } | ConvertTo-Json
Invoke-MgGraphRequest -Method POST -Uri "https://graph.microsoft.com/v1.0/domains" -Body $body -ContentType "application/json"

# Verify domain was added
Get-MgDomain -DomainId "fe.learningtalent.co.uk"
```

## Step 4: Configure Email Settings

### 4.1 Set Up Email Routing
1. Go to Microsoft 365 admin center
2. Navigate to Settings → Domains
3. Select `fe.learningtalent.co.uk`
4. Configure email settings

### 4.2 Create User Accounts or Shared Mailboxes
```powershell
# Create shared mailbox
New-Mailbox -Shared -Name "FE Team" -DisplayName "FE Team" -Alias "feteam"

# Or create user account
New-MgUser -DisplayName "FE User" -MailNickname "feuser" -UserPrincipalName "feuser@fe.learningtalent.co.uk" -Password (ConvertTo-SecureString "TempPassword123!" -AsPlainText -Force) -AccountEnabled
```

## Troubleshooting

### If DNS verification fails:
1. Wait 5-10 minutes for DNS propagation
2. Check DNS records are correct
3. Try different subdomain name (mail, outreach, campaigns)

### If domain addition fails:
1. Check if subdomain is already added
2. Try via different method (Admin Center vs PowerShell)
3. Check for federation conflicts

### If email doesn't work:
1. Verify MX records are correct
2. Check Exchange Online configuration
3. Test with different email client

## Expected Results
- Domain shows as "Verified" in Microsoft 365 admin center
- DNS records resolve correctly
- Email addresses work (e.g., test@fe.learningtalent.co.uk)
- Can send/receive emails from the subdomain