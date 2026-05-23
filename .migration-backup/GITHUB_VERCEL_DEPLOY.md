# GitHub + Vercel Deployment Guide

Your MVP is ready. Follow these exact steps to go live.

---

## Step 1: Create GitHub Repository

**Time: 2 minutes**

1. Go to **https://github.com/new**
2. Fill in:
   - **Repository name**: `ai-undetectable`
   - **Description**: `Make AI-generated images undetectable`
   - **Public** (so we can launch it)
   - **Do NOT** initialize with README (we have one)
3. Click **"Create repository"**

You'll see a screen like:
```
…or push an existing repository from the command line

git remote add origin https://github.com/bradleybeatz1313/ai-undetectable.git
git branch -M main
git push -u origin main
```

Keep that page open. You'll use those commands next.

---

## Step 2: Push Code to GitHub

**Time: 5 minutes**

The code is already committed locally. Just push it:

```bash
cd /agent/workspace/ai-undetectable

# Rename branch to main
git branch -M main

# Add GitHub remote (copy from your GitHub repo page above)
git remote add origin https://github.com/bradleybeatz1313/ai-undetectable.git

# Push to GitHub
git push -u origin main
```

**You'll be prompted for credentials:**
- Username: `bradleybeatz1313`
- Password: Use a **Personal Access Token** (not your GitHub password)

**To create a Personal Access Token:**
1. Go to **https://github.com/settings/tokens/new**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Name: `ai-undetectable-deploy`
4. Select scope: **`repo`** (full control of private repositories)
5. Click **"Generate token"** and copy it
6. Paste as password when git asks

**Expected output:**
```
Enumerating objects: 15, done.
...
To https://github.com/bradleybeatz1313/ai-undetectable.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

✅ **Code is now on GitHub!** Verify at: https://github.com/bradleybeatz1313/ai-undetectable

---

## Step 3: Deploy to Vercel

**Time: 5 minutes (automatic)**

Vercel auto-detects Dockerfile + FastAPI and deploys instantly.

### Option A: Web UI (Easiest)

1. Go to **https://vercel.com/dashboard**
2. Click **"Add New..."** → **"Project"**
3. Select **"Import Git Repository"**
4. Search for `ai-undetectable` and select it
5. **Vercel auto-detects:**
   - Framework: Python/FastAPI
   - Build Command: (uses Dockerfile)
   - Output Directory: (handled by Docker)
6. **Add Environment Variables:**
   - Click **"Add New"** button
   - **Name**: `DATABASE_URL`
   - **Value**: `sqlite:///./ai_undetectable.db`
   - (Leave `STRIPE_SECRET_KEY` blank for now)
7. Click **"Deploy"** and wait ~2 minutes

**Your site goes live at:**
```
https://ai-undetectable-<random>.vercel.app
```

### Option B: CLI (If you prefer terminal)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd /agent/workspace/ai-undetectable
vercel --prod

# Follow the prompts:
# - Link to existing project? → No (create new)
# - Project name → ai-undetectable
# - Which directory? → (press enter for current)
# - Deploy? → Yes
```

**Expected output:**
```
✓ Linked to bradleybeatz1313/ai-undetectable
✓ Built in 45s
✓ Deployment ready
https://ai-undetectable-abc123.vercel.app
```

---

## Step 4: Test Live API

**Time: 2 minutes**

Your API is live! Test it:

```bash
API_URL="https://ai-undetectable-abc123.vercel.app"  # Replace with your URL

# 1. Health check
curl $API_URL/health

# 2. Interactive docs
# Visit: $API_URL/docs (in browser)

# 3. Sign up
curl -X POST $API_URL/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "youremail@example.com"}'

# 4. Process an image
curl -X POST $API_URL/process \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@test_image.jpg"
```

✅ **API is live and working!**

---

## Step 5: Set Up Custom Domain (Optional)

**Time: 10 minutes**

Want `aidetectable.com` instead of `vercel.app`?

1. Buy domain (GoDaddy, Namecheap, etc.) — ~$12/year
2. In Vercel Project Settings → **Domains**
3. Add your domain
4. Vercel shows DNS records to add
5. Add records in your domain registrar
6. Wait ~5-15 minutes for DNS propagation

**Example domain:** `api.aidetectable.com` → your Vercel deployment

---

## Step 6: Enable Auto-Deployments

**Already set up!** Every time you push to GitHub's `main` branch, Vercel automatically redeploys. No action needed.

To test:
```bash
cd /agent/workspace/ai-undetectable
git add .
git commit -m "Update: improve image processing"
git push origin main
```

Vercel auto-deploys in ~60 seconds. Check: **https://vercel.com/dashboard**

---

## Next Steps (Post-Launch)

### Immediate (Week 1)
- [ ] Validate algorithm on ZeroGPT.com (does it actually work?)
- [ ] Share URL on X (@beatzbradley) + r/Decentral, r/SideProject
- [ ] Collect free signups (track in Google Sheet)

### Soon (Week 2)
- [ ] Integrate Stripe billing (edit `/upgrade-to-pro` endpoint)
- [ ] Add landing page analytics (Google Analytics)
- [ ] Custom domain setup
- [ ] Database migration: SQLite → PostgreSQL (if scaling)

### Growth (Week 3+)
- [ ] Email free users → "Upgrade to Pro"
- [ ] Monitor unit economics
- [ ] Iterate on algorithm based on feedback

---

## Troubleshooting

### "git push" fails with "failed to authenticate"
- Use a **Personal Access Token** as password (not GitHub password)
- Token scope must include `repo`
- Get one at: https://github.com/settings/tokens/new

### Vercel deployment fails
- Check build logs: https://vercel.com/dashboard
- Common issues:
  - Missing `Dockerfile` (it's included, you're fine)
  - Wrong environment variables (we only need `DATABASE_URL`)
  - Database file permissions (SQLite handles this)

### API returns 502 Bad Gateway
- Your Vercel deployment is still building. Wait 2-3 minutes.
- Check: https://vercel.com/dashboard → Deployments tab

### Can't see environment variables in Vercel
- Go to Project Settings → Environment Variables
- Scroll down to see all variables
- Redeploy after adding new ones

---

## Success Checklist

- [ ] GitHub repo created
- [ ] Code pushed to GitHub
- [ ] Vercel deployment live
- [ ] API responds to `/health`
- [ ] API docs visible at `/docs`
- [ ] Can sign up and process images
- [ ] Custom domain set (optional)

---

## Your Live API

```
Endpoint: https://ai-undetectable-abc123.vercel.app
Docs: https://ai-undetectable-abc123.vercel.app/docs
Status: https://vercel.com/dashboard
```

**You're live. 🚀**

---

## Questions?

- Vercel docs: https://vercel.com/docs
- GitHub docs: https://docs.github.com
- FastAPI on Vercel: https://vercel.com/docs/functions/python

---

**Next: Test on ZeroGPT to validate the algorithm actually works.**
