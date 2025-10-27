# Smart Security - RTSP Camera Streaming

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy to Render](https://img.shields.io/badge/deploy-render-46e3b7.svg)](https://render.com)

A modern web-based RTSP camera streaming application with a sleek dark UI, built with Flask and OpenCV.

## ✨ Features

- 📹 **RTSP Camera Streaming** - Connect to any RTSP camera
- 🎥 **Video File Playback** - Stream local video files
- 📊 **Real-time FPS Monitoring** - Performance tracking
- 🎨 **Shadcn-inspired Dark UI** - Modern, clean interface
- 🔄 **Auto-looping** - Videos automatically restart
- 🚀 **Production Ready** - Optimized for deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Local Development

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd smartsecurity
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python3 detecciones.py
```

4. **Open your browser:**
```
http://127.0.0.1:8080
```

## 📦 Deployment

### One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Using Deploy Script

```bash
./deploy.sh
```

Choose your preferred platform:
1. **Render** (Free tier) - Recommended
2. **Railway** ($5 credit)
3. **Heroku** ($7/month)

### Manual Deployment

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for detailed instructions.

## 🎥 Usage

1. Enter your RTSP camera URL in the format:
```
rtsp://username:password@ip:port/stream
```

2. Click "Start Stream" to begin viewing

3. Click "Stop Stream" to end the session

## RTSP URL Examples

- Generic: `rtsp://username:password@192.168.1.100:554/stream`
- Hikvision: `rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101`
- Dahua: `rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0`
- TP-Link: `rtsp://admin:password@192.168.1.100:554/stream1`

## Tech Stack

- **Backend**: Flask (Python)
- **Video Processing**: OpenCV
- **Deployment**: Gunicorn (WSGI server)
- **Frontend**: Vanilla JavaScript, Shadcn-inspired CSS

## Notes

- For production deployment, use platforms like Render, Railway, or DigitalOcean
- Vercel is NOT suitable for this application (no long-running processes support)
- Free tier on Render may have limitations on video streaming performance

## License

MIT
