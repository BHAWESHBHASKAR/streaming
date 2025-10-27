# 🚀 Deployment Guide

## RTSP Links (Local Testing)
- **Local RTSP**: `rtsp://127.0.0.1:8554/camera`
- **Network RTSP**: `rtsp://192.168.1.11:8554/camera`
- **Web UI**: `http://127.0.0.1:8080`

---

## ⚠️ Important: Vercel Won't Work!

This app requires:
- Long-running processes (video streaming)
- OpenCV (system-level library)
- Persistent connections
- Background processes

**Vercel only supports serverless functions** ❌

---

## ✅ Deploy to Render (Recommended)

### Quick Deploy (2 minutes)

1. **Push to GitHub**
```bash
cd /Users/rishavkumarraman/Desktop/freelance/smartsecurity
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. **Deploy on Render**
   - Go to: https://dashboard.render.com/
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Click **"Apply"**
   - Done! 🎉

### Manual Deploy (Alternative)

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repo
4. Configure:
   - **Name**: `smart-security`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 detecciones:app`
   - **Plan**: Free
5. Click **"Create Web Service"**

---

## 🔧 Alternative Platforms

### Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### DigitalOcean App Platform
1. Go to: https://cloud.digitalocean.com/apps
2. Click **"Create App"**
3. Connect GitHub
4. Select repository
5. Deploy (uses Procfile automatically)

### Heroku
```bash
heroku login
heroku create smart-security-app
git push heroku main
```

---

## 📝 Files Created for Deployment

✅ `requirements.txt` - Python dependencies
✅ `render.yaml` - Render configuration (Blueprint)
✅ `Procfile` - Process file for Heroku/Railway
✅ `runtime.txt` - Python version
✅ `.gitignore` - Files to exclude from git
✅ `README.md` - Project documentation

---

## 🎥 RTSP URL Examples

Once deployed, users can enter:

**Generic Format:**
```
rtsp://username:password@camera-ip:port/stream
```

**Common Cameras:**
- **Hikvision**: `rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101`
- **Dahua**: `rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0`
- **TP-Link**: `rtsp://admin:password@192.168.1.100:554/stream1`
- **Amcrest**: `rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=1`
- **Reolink**: `rtsp://admin:password@192.168.1.100:554/h264Preview_01_main`

---

## 💡 Performance Notes

- **Free Tier**: Works fine for single user/camera
- **Paid Tier**: Better for multiple concurrent streams
- **Latency**: Expect 2-5 seconds delay (normal for RTSP over internet)
- **Bandwidth**: ~1-3 Mbps per camera stream

---

## 🐛 Troubleshooting

### Can't connect to RTSP camera?
- Check camera is on same network
- Verify RTSP port is open (usually 554)
- Try VLC to test: `vlc rtsp://your-camera-url`
- Check username/password

### Deployment fails?
- Check build logs in Render dashboard
- Ensure all files are committed to git
- Verify `requirements.txt` is present

### Stream is slow?
- Try lower resolution stream URL (subtype=1 instead of 0)
- Check internet upload speed
- Consider upgrading to paid tier

---

## 📞 Support

If you need help:
1. Check Render logs: Dashboard → Your Service → Logs
2. Test RTSP URL locally first with VLC
3. Verify camera network settings
