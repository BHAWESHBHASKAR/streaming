# 🚀 GitHub & Render Deployment Guide

## ✅ Code is Ready! Now Deploy in 10 Minutes

---

## Step 1: Push to GitHub (5 minutes)

### A. Create Repository on GitHub

1. Go to: **https://github.com/BHAWESHBHASKAR/streaming**
2. If repository doesn't exist:
   - Go to: **https://github.com/new**
   - Repository name: `streaming`
   - Description: `Smart Security Camera Streaming System`
   - Visibility: **Public** (required for Render free tier)
   - **DO NOT** check "Initialize with README" (we already have files)
   - Click **"Create repository"**

### B. Push Your Code

Your code is already committed locally. Just push it:

```bash
# If repository exists but is empty, force push:
git push -u origin main --force

# If you get authentication error, use Personal Access Token:
# 1. Go to: https://github.com/settings/tokens
# 2. Generate new token (classic)
# 3. Select: repo (all), workflow
# 4. Copy token
# 5. Use this command instead:
git remote set-url origin https://YOUR_TOKEN@github.com/BHAWESHBHASKAR/streaming.git
git push -u origin main
```

### C. Verify on GitHub

Go to: **https://github.com/BHAWESHBHASKAR/streaming**

You should see:
- ✅ 17 files
- ✅ README.md displayed
- ✅ render.yaml present
- ✅ All deployment files

---

## Step 2: Deploy to Render (5 minutes)

### Method 1: Blueprint (Recommended - Automatic)

1. **Go to Render Dashboard**
   - Visit: **https://dashboard.render.com/**
   - Sign up/Login (use GitHub for easy access)

2. **Create New Blueprint**
   - Click **"New +"** button (top right)
   - Select **"Blueprint"**
   
3. **Connect GitHub Repository**
   - Click **"Connect GitHub"** (if not already connected)
   - Authorize Render to access your repositories
   - Search for: `streaming`
   - Select: **BHAWESHBHASKAR/streaming**
   - Click **"Connect"**

4. **Deploy**
   - Render will auto-detect `render.yaml` ✅
   - Review the configuration:
     ```yaml
     Service Name: smart-security
     Environment: Python 3.11
     Plan: Free
     ```
   - Click **"Apply"** or **"Create Blueprint"**

5. **Wait for Build**
   - Build process: ~3-5 minutes
   - Watch logs in real-time
   - Status will change: Building → Deploying → Live ✅

6. **Get Your URL**
   - Once deployed, you'll get a URL like:
   - `https://smart-security-xxxx.onrender.com`
   - Click to open your live app! 🎉

---

### Method 2: Manual Web Service (Alternative)

If Blueprint doesn't work:

1. **Go to Render Dashboard**
   - Visit: **https://dashboard.render.com/**

2. **Create Web Service**
   - Click **"New +"** → **"Web Service"**
   - Connect GitHub repository: `BHAWESHBHASKAR/streaming`

3. **Configure Service**
   ```
   Name:           smart-security
   Environment:    Python 3
   Region:         Oregon (US West) - or closest to you
   Branch:         main
   Root Directory: (leave empty)
   
   Build Command:  pip install -r requirements.txt
   Start Command:  gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 detecciones:app
   
   Plan:           Free
   ```

4. **Advanced Settings** (Click to expand)
   ```
   Auto-Deploy:    Yes (recommended)
   Health Check:   /status
   ```

5. **Click "Create Web Service"**

6. **Wait for Deployment**
   - First build takes ~3-5 minutes
   - Watch build logs for any errors
   - Once complete, your app is live!

---

## Step 3: Test Your Deployment (2 minutes)

### A. Open Your App

Visit: `https://your-app-name.onrender.com`

You should see:
- ✅ Beautiful dark UI
- ✅ RTSP URL input field pre-filled
- ✅ Start/Stop buttons
- ✅ Status indicator

### B. Test Streaming

1. **Use Test RTSP Stream** (if available):
   ```
   rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4
   ```

2. **Or Use Your Camera**:
   ```
   rtsp://username:password@your-camera-ip:554/stream
   ```

3. **Click "Start Stream"**
   - Video should appear within 5-10 seconds
   - FPS counter should show at top
   - Status should show "Streaming"

### C. Test Health Endpoint

```bash
# From your terminal:
curl https://your-app-name.onrender.com/status

# Should return:
{
  "status": "Ready",
  "is_running": false,
  "fps": 0
}
```

---

## 🎯 Important Notes

### Render Free Tier Limitations

✅ **What You Get:**
- 750 hours/month (enough for hobby projects)
- Automatic HTTPS/SSL
- Auto-deploy on GitHub push
- Environment variables support

⚠️ **Limitations:**
- **Spins down after 15 minutes** of inactivity
- **Cold start**: Takes 30-60 seconds to wake up
- **Limited bandwidth**: Good for testing, not heavy use
- **Shared resources**: Performance can vary

### Making it Production-Ready

For production use, **upgrade to paid plan** ($7-20/month):

1. **Go to Service Settings**
2. **Upgrade Plan**:
   - **Starter** ($7/mo): 512MB RAM, always-on
   - **Standard** ($25/mo): 2GB RAM, better performance

Benefits:
- ✅ Always-on (no sleep)
- ✅ Faster performance
- ✅ More bandwidth
- ✅ Priority support

---

## 🔧 Post-Deployment Configuration

### Environment Variables (Optional)

If you want to customize:

1. **Go to Service Dashboard**
2. **Environment** tab
3. **Add Variables**:
   ```
   CONFIDENCE_THRESHOLD=0.7
   FRAME_SKIP=0
   DEBUG=False
   ```

### Custom Domain (Optional)

1. **Go to Service Settings**
2. **Custom Domain** section
3. **Add your domain**: `stream.yourdomain.com`
4. **Update DNS** with provided CNAME record
5. **HTTPS** is automatic!

### Auto-Deploy on Push

Already configured! Just:
```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main
```
Render will automatically rebuild and deploy! 🚀

---

## 📊 Monitoring Your App

### Check Logs

1. **Render Dashboard** → Your Service → **Logs** tab
2. **View real-time logs**:
   - Application startup
   - Incoming requests
   - Errors and warnings

### Health Monitoring

Use UptimeRobot (free):
1. Go to: **https://uptimerobot.com**
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://your-app.onrender.com/status`
   - Interval: 5 minutes
3. Get alerts when app is down

### Performance Metrics

In Render Dashboard:
- **Metrics** tab shows:
  - CPU usage
  - Memory usage
  - Request count
  - Response time

---

## 🐛 Troubleshooting

### Build Fails

**Check build logs**:
```
Error: Could not find opencv-python-headless
```
**Solution**: Verify `requirements.txt` is correct (already done ✅)

---

### App Won't Start

**Check logs for**:
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Rebuild service (click "Manual Deploy" → "Clear build cache & deploy")

---

### Can't Connect to Camera

**Common issues**:
- ❌ Camera behind firewall/NAT
- ❌ Wrong RTSP URL format
- ❌ Camera requires authentication

**Test locally first**:
```bash
vlc rtsp://your-camera-url
```

---

### Slow Performance

**On Free Tier**:
- App sleeps after 15 min
- Cold start takes 30-60 seconds
- Limited bandwidth

**Solutions**:
1. Upgrade to paid tier ($7/mo)
2. Keep app warm with cron job:
   ```bash
   # Use cron-job.org to ping every 10 min
   https://your-app.onrender.com/status
   ```

---

## ✅ Deployment Checklist

- [x] Code committed to Git
- [ ] Repository created on GitHub
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] GitHub connected to Render
- [ ] Blueprint/Service deployed
- [ ] App tested and working
- [ ] Health monitoring setup (optional)
- [ ] Custom domain configured (optional)

---

## 🎊 Success!

Your app is now live at:
**https://your-app-name.onrender.com**

### Share Your App

Give users these instructions:
```
1. Visit: https://your-app-name.onrender.com
2. Enter RTSP camera URL:
   rtsp://username:password@camera-ip:554/stream
3. Click "Start Stream"
4. Watch your camera feed!
```

---

## 📞 Need Help?

### Documentation
- **Render Docs**: https://render.com/docs
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/
- **Project Docs**: See START_HERE.md

### Support
- **Render Support**: https://render.com/support
- **GitHub Issues**: https://github.com/BHAWESHBHASKAR/streaming/issues

---

## 🚀 Next Steps

1. ✅ Test with real cameras
2. ✅ Add authentication (security)
3. ✅ Set up monitoring
4. ✅ Upgrade to paid plan for production
5. ✅ Add custom domain
6. ✅ Share with users!

---

**Congratulations! Your Smart Security Camera System is live! 🎉**

Made with ❤️ using Flask, OpenCV, and Render
