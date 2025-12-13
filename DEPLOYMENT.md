# HotPuppy Deployment Guide

Complete guide to deploying HotPuppy to AWS App Runner with hotpuppy.net domain.

## Prerequisites

- GitHub account with hotpuppy repository
- AWS account with appropriate permissions
- Domain hotpuppy.net (already owned)

## Step 1: Push to GitHub

If you haven't already, create the GitHub repository:

```bash
cd /home/user/hotpuppy

# Create repo on GitHub (via web or CLI)
# Then add remote and push:
git remote add origin https://github.com/YOUR_USERNAME/hotpuppy.git
git push -u origin main
```

## Step 2: Set Up AWS App Runner Service

### 2.1 Create Service

1. Open AWS Console → App Runner
2. Click **"Create service"**

### 2.2 Source Configuration

- **Source**: Repository
- **Repository type**: GitHub
- **Connect to GitHub** (authorize if first time)
- **Repository**: Select `YOUR_USERNAME/hotpuppy`
- **Branch**: `main`
- **Deployment trigger**: Automatic (deploys on every push)
- Click **Next**

### 2.3 Build Configuration

- **Configuration file**: Use configuration file
- File: `apprunner.yaml` (automatically detected)
- Click **Next**

### 2.4 Service Configuration

- **Service name**: `hotpuppy-service` (or your preference)
- **Virtual CPU**: 1 vCPU (start small, scale later)
- **Virtual memory**: 2 GB
- **Environment variables**:
  - Click **Add environment variable**
  - Name: `OPENAI_API_KEY`
  - Value: `your-openai-api-key-here` (or leave empty for placeholder images)
- **Auto scaling**:
  - Min instances: 1
  - Max instances: 3 (for low traffic)
  - Concurrency: 100

### 2.5 Health Check

- **Protocol**: HTTP
- **Path**: `/health`
- **Interval**: 5 seconds
- **Timeout**: 2 seconds
- **Healthy threshold**: 1
- **Unhealthy threshold**: 5

### 2.6 Security

- **Instance role**: Create new service role (automatic)

Click **Next** → **Create & deploy**

⏱️ **Wait 5-10 minutes** for the service to deploy.

## Step 3: Test the App Runner URL

Once deployed:

1. Copy the default App Runner URL (e.g., `https://abc123.us-east-1.awsapprunner.com`)
2. Open it in your browser
3. You should see a puppy image!

## Step 4: Configure Custom Domain (hotpuppy.net)

### 4.1 Verify Domain Ownership in Route53

1. Go to **Route53** → **Hosted zones**
2. Check if `hotpuppy.net` exists
   - **If YES**: Note the hosted zone ID
   - **If NO**: Create hosted zone:
     - Click **Create hosted zone**
     - Domain name: `hotpuppy.net`
     - Type: Public hosted zone
     - Click **Create**
     - **IMPORTANT**: Update your domain registrar's nameservers to use Route53's NS records

### 4.2 Link Domain in App Runner

1. Go to App Runner service → **Custom domains** tab
2. Click **Link domain**
3. Enter domains:
   - `hotpuppy.net`
   - `www.hotpuppy.net`
4. Click **Next**

### 4.3 Add Validation Records to Route53

App Runner will show validation records (CNAME records):

1. Go to **Route53** → **Hosted zones** → `hotpuppy.net`
2. For each validation record:
   - Click **Create record**
   - Record type: CNAME
   - Name: (copy from App Runner, e.g., `_validation.hotpuppy.net`)
   - Value: (copy from App Runner)
   - TTL: 300
   - Click **Create records**

⏱️ **Wait 5-10 minutes** for validation to complete.

### 4.4 Create ALIAS Records for Your Domain

After validation succeeds, App Runner shows target domains. Create these records:

**For hotpuppy.net:**
1. Route53 → Hosted zones → hotpuppy.net → Create record
2. Record name: (leave empty for root domain)
3. Record type: A
4. Alias: YES
5. Route traffic to:
   - Alias to App Runner service
   - Region: (your region)
   - Service: hotpuppy-service
6. Create records

**For www.hotpuppy.net:**
1. Create record
2. Record name: `www`
3. Record type: A
4. Alias: YES
5. Route traffic to:
   - Alias to App Runner service
   - Region: (your region)
   - Service: hotpuppy-service
6. Create records

### 4.5 Verify Domain

After DNS propagation (5-30 minutes):

```bash
# Test DNS resolution
dig hotpuppy.net
dig www.hotpuppy.net

# Test in browser
open https://hotpuppy.net
open https://www.hotpuppy.net
```

Both should show your HotPuppy site with HTTPS! 🎉

## Step 5: Enable AI Image Generation (Optional)

### 5.1 Get OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up / Log in
3. Go to API keys → Create new secret key
4. Copy the key (starts with `sk-...`)

### 5.2 Update App Runner Environment Variable

1. App Runner → hotpuppy-service → Configuration tab
2. Find **Environment variables** section
3. Edit `OPENAI_API_KEY`
4. Paste your API key
5. Click **Save** → **Deploy**

⏱️ Wait for redeploy (~5 minutes)

Now your site will generate AI puppy images using DALL-E 3!

## Step 6: Monitor and Manage

### Logs

App Runner → hotpuppy-service → Logs tab
- View application logs
- Debug issues
- Monitor traffic

### Metrics

App Runner → hotpuppy-service → Metrics tab
- HTTP requests
- Response time
- Instance count

### Cost Monitoring

- **App Runner**: ~$5-10/month (1 instance @ 1vCPU, 2GB)
- **Route53**: $0.50/month (hosted zone)
- **DALL-E API**: $0.04 per image (if enabled)

## Continuous Deployment

Any push to `main` branch automatically deploys:

```bash
cd /home/user/hotpuppy
# Make changes
git add .
git commit -m "Update feature"
git push origin main
```

App Runner will automatically build and deploy! 🚀

## Troubleshooting

### Service won't start
- Check Logs tab for errors
- Verify apprunner.yaml syntax
- Ensure requirements.txt has correct versions

### Domain not working
- Verify Route53 nameservers match registrar
- Check ALIAS record configuration
- Wait for DNS propagation (up to 48h)

### AI images not generating
- Verify OPENAI_API_KEY is set correctly
- Check OpenAI account has credits
- Review logs for API errors

## Scaling

As traffic grows:

1. App Runner → Configuration → Auto scaling
2. Increase max instances (e.g., 10)
3. Adjust concurrency if needed
4. Monitor costs in AWS Cost Explorer

## Security

- App Runner handles HTTPS automatically
- Keep OPENAI_API_KEY secure (never commit to Git)
- Consider adding rate limiting for high traffic
- Enable AWS WAF if needed

---

## Quick Reference Commands

```bash
# Local development
cd /home/user/hotpuppy
uvicorn main:app --reload

# Git operations
git status
git add .
git commit -m "message"
git push origin main

# Test endpoints
curl https://hotpuppy.net/health
curl https://hotpuppy.net/api/new-puppy
```

## Support

- HotPuppy GitHub: Issues tab
- AWS App Runner Docs: https://docs.aws.amazon.com/apprunner/
- OpenAI API Docs: https://platform.openai.com/docs
