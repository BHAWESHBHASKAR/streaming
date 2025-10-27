# 🚀 Deployment Checklist

## Pre-Deployment Verification

### ✅ Required Files
- [x] `detecciones.py` - Main application file
- [x] `requirements.txt` - Python dependencies
- [x] `runtime.txt` - Python version (3.11.0)
- [x] `Procfile` - Process definition for Heroku/Railway
- [x] `render.yaml` - Render Blueprint configuration
- [x] `.gitignore` - Excludes unnecessary files
- [x] `README.md` - Project documentation
- [x] `DEPLOYMENT.md` - Deployment guide

### ✅ Code Verification
- [x] No hardcoded passwords or API keys
- [x] Environment-based port configuration (`PORT` env var)
- [x] Production/development mode detection
- [x] Error handling for RTSP streams
- [x] CORS enabled for cross-origin requests
- [x] Optimized buffer settings for video streaming

### ✅ Git Repository
```bash
# Initialize git repository
git init

# Add all files (respecting .gitignore)
git add .

# Commit changes
git commit -m "Initial commit - Smart Security Camera System"

# Add remote (create repo on GitHub first)
git remote add origin https://github.com/YOUR_USERNAME/smart-security.git

# Push to GitHub
git push -u origin main
```

---

## Deployment Options

### 🎯 Option 1: Render (Recommended - Easiest)

**Method A: Blueprint (Automatic)**
1. Push code to GitHub
2. Go to https://dashboard.render.com/
3. Click **"New +"** → **"Blueprint"**
4. Connect GitHub repo
5. Render auto-detects `render.yaml` ✅
6. Click **"Apply"**

**Method B: Manual Setup**
1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repo
4. Configure:
   - **Name**: smart-security
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 detecciones:app`
   - **Plan**: Free (or Starter for better performance)
5. Click **"Create Web Service"**

**Render Free Tier Limits:**
- ✅ 750 hours/month
- ✅ Auto-sleep after 15 min inactivity
- ⚠️ Cold starts (takes 30-60s to wake up)

---

### 🚂 Option 2: Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Open in browser
railway open
```

**Railway Limits:**
- ✅ $5 free credit/month
- ✅ Always-on (no sleep)
- ✅ Better performance than Render free tier

---

### 🌊 Option 3: DigitalOcean App Platform

1. Go to https://cloud.digitalocean.com/apps
2. Click **"Create App"**
3. Connect GitHub
4. Select repository
5. Configure:
   - **Type**: Web Service
   - **Run Command**: `gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 detecciones:app`
6. Click **"Next"** → **"Launch App"**

**DO App Platform:**
- ✅ $5/month (no free tier)
- ✅ Better performance
- ✅ More reliable for production

---

### 🔵 Option 4: Heroku

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create smart-security-cam

# Deploy
git push heroku main

# Open app
heroku open
```

**Heroku Limits:**
- ⚠️ No free tier (since Nov 2022)
- 💰 Starts at $7/month (Eco Dynos)

---

## Post-Deployment

### ✅ Test Your Deployment

1. **Check Health Endpoint**
   ```bash
   curl https://your-app-url.com/status
   ```
   Should return JSON with `is_running` status

2. **Test RTSP Streaming**
   - Open web UI: `https://your-app-url.com`
   - Enter an RTSP URL (your camera)
   - Click "Start Stream"
   - Verify video appears

3. **Monitor Logs**
   - **Render**: Dashboard → Your Service → Logs
   - **Railway**: `railway logs`
   - **Heroku**: `heroku logs --tail`

### ⚙️ Environment Variables (if needed)

Add these in your platform's dashboard:

```bash
# Optional - if you want to enable object detection
MODEL_ARMS_PATH=gun_detectionultimo.pt
MODEL_HELMET_PATH=helmet_detectionultimo.pt

# Optional - custom video path
DEFAULT_VIDEO_PATH=/app/videos/demo.mp4
```

---

## 🐛 Troubleshooting

### Build Fails
- ✅ Check `requirements.txt` is present
- ✅ Verify Python version in `runtime.txt`
- ✅ Check build logs for missing dependencies

### App Crashes on Start
- ✅ Check start command in Procfile/render.yaml
- ✅ Verify `detecciones:app` points to correct Flask app
- ✅ Check logs for error messages

### Can't Connect to RTSP Camera
- ✅ Camera must be publicly accessible (not behind NAT)
- ✅ Use public IP or domain name
- ✅ Verify RTSP port (554) is open
- ✅ Test locally with VLC first

### Slow Performance
- ✅ Upgrade to paid tier (free tiers have limits)
- ✅ Reduce video resolution in RTSP URL
- ✅ Use subtype=1 (lower quality) instead of 0

---

## 🔐 Security Recommendations

### For Production Use:

1. **Add Authentication**
   ```python
   # Add to detecciones.py
   from flask_httpauth import HTTPBasicAuth
   auth = HTTPBasicAuth()
   
   @auth.verify_password
   def verify_password(username, password):
       return username == os.environ.get('ADMIN_USER') and \
              password == os.environ.get('ADMIN_PASS')
   
   @app.route('/')
   @auth.login_required
   def index():
       return render_template('index.html')
   ```

2. **Use HTTPS** (automatic on Render/Railway/Heroku)

3. **Add Rate Limiting**
   ```bash
   pip install flask-limiter
   ```

4. **Set Secure Headers**
   ```bash
   pip install flask-talisman
   ```

---

## 📊 Performance Optimization

### For Better Streaming:

1. **Increase Workers** (on paid tiers):
   ```yaml
   # render.yaml
   startCommand: gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 detecciones:app
   ```

2. **Add Redis Caching** (for multiple users):
   ```bash
   pip install redis flask-caching
   ```

3. **Use CDN** (for static assets):
   - Cloudflare (free)
   - AWS CloudFront

---

## 📝 Maintenance

### Regular Updates:
```bash
# Update dependencies
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

### Monitoring:
- Set up uptime monitoring: https://uptimerobot.com (free)
- Check logs regularly for errors
- Monitor bandwidth usage

---

## ✅ Deployment Complete!

Your app is now live at: `https://your-app-url.com`

**Next Steps:**
1. ⭐ Star the repository
2. 📝 Update README with your deployment URL
3. 🎥 Test with real RTSP cameras
4. 📊 Monitor performance and logs
5. 🔄 Set up CI/CD for automatic deployments

---

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Flask Docs**: https://flask.palletsprojects.com
- **OpenCV Issues**: Check camera compatibility

Good luck! 🚀
