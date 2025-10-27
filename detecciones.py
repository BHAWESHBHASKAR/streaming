#!/usr/bin/env python3
"""
Simple Video File Streamer
Streams a local video file as if it were an RTSP/webcam stream
Uses a file path instead of RTSP URL
"""

import cv2
import torch
from ultralytics import YOLO
import time
import socket
import struct
import threading
from flask import Flask, render_template, Response, request, jsonify
from flask_cors import CORS
import os

device = "cuda" if torch.cuda.is_available() else "cpu"

# Modelos
model_arms = None
model_helmet = None

CONFIDENCE_THRESHOLD = 0.7
TARGET_CLASSES_ARMS = [0]
TARGET_CLASSES_HELMETS = [0]

app = Flask(__name__)
CORS(app)

class VideoStream:
    def __init__(self):
        self.cap = None
        self.is_running = False
        self.counter_arms = 0
        self.counter_helmet = 0
        self.frame_skip = 0
        self.frame_count = 0
        self.current_fps = 0
        self.video_source = ""
        self.status = "Ready"
        self.loop_video = True  # Loop the video when it ends
        
    def start_stream(self, video_source):
        if self.is_running:
            return False, "Stream is already running"
        
        # Load models if not already loaded
        global model_arms, model_helmet
        if model_arms is None or model_helmet is None:
            try:
                self.status = "Loading models..."
                # Update paths or comment out if models don't exist
                # model_arms = YOLO("gun_detectionultimo.pt").to(device)
                # model_helmet = YOLO("helmet_detectionultimo.pt").to(device)
                print("⚠️ Models not loaded - detection disabled. Update model paths to enable.")
            except Exception as e:
                self.status = "Model loading failed"
                return False, f"Failed to load models: {str(e)}"
        
        try:
            self.status = "Connecting to video source..."
            
            # Check if it's a file path or RTSP URL
            if os.path.isfile(video_source):
                print(f"📁 Loading video file: {video_source}")
                self.cap = cv2.VideoCapture(video_source)
            else:
                print(f"🌐 Connecting to stream: {video_source}")
                # Use RTSP with optimized settings for network streams
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|buffer_size;1024000"
                self.cap = cv2.VideoCapture(video_source, cv2.CAP_FFMPEG)
            
            # Set buffer and thread settings
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
            
            if not self.cap.isOpened():
                raise Exception("Unable to open video source")
            
            self.is_running = True
            self.video_source = video_source
            self.status = "Streaming..."
            return True, "Stream started successfully"
            
        except Exception as e:
            self.status = "Connection failed"
            if self.cap:
                self.cap.release()
            return False, f"Failed to connect: {str(e)}"
    
    def stop_stream(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.status = "Stopped"
        self.current_fps = 0
        
    def generate_frames(self):
        while self.is_running and self.cap:
            try:
                start_time = time.time()
                ret, frame = self.cap.read()
                
                # If video ends and loop is enabled, restart it
                if not ret:
                    if self.loop_video and os.path.isfile(self.video_source):
                        print("🔄 Restarting video loop...")
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        self.stop_stream()
                        break
                
                self.frame_count += 1
                if self.frame_count % (self.frame_skip + 1) != 0:
                    continue
                
                # Process frame with models if available
                annotated_frame = frame.copy()
                
                if model_arms is not None and model_helmet is not None:
                    try:
                        # Inferencias
                        results_arms = model_arms.predict(source=frame, imgsz=416, conf=CONFIDENCE_THRESHOLD, verbose=False)
                        results_helmet = model_helmet.predict(source=frame, imgsz=416, conf=CONFIDENCE_THRESHOLD, verbose=False)
                        
                        # Filtrar clases
                        boxes_arms = results_arms[0].boxes
                        keep_arms = [i for i, cls in enumerate(boxes_arms.cls) if int(cls) in TARGET_CLASSES_ARMS]
                        results_arms[0].boxes = boxes_arms[keep_arms]
                        
                        boxes_helmet = results_helmet[0].boxes
                        keep_helmet = [i for i, cls in enumerate(boxes_helmet.cls) if int(cls) in TARGET_CLASSES_HELMETS]
                        results_helmet[0].boxes = boxes_helmet[keep_helmet]
                        
                        annotated_frame = results_arms[0].plot(img=annotated_frame)
                        annotated_frame = results_helmet[0].plot(img=annotated_frame)
                        
                        # Contadores de detección
                        if len(results_arms[0].boxes) > 0:
                            self.counter_arms += 1
                        else:
                            self.counter_arms = 0
                        
                        if len(results_helmet[0].boxes) > 0:
                            self.counter_helmet += 1
                        else:
                            self.counter_helmet = 0
                        
                        # 🚨 Enviar alerta al bot cada 5 detecciones
                        if self.counter_arms == 5 or self.counter_helmet == 5:
                            resized = cv2.resize(annotated_frame, (640, 480))
                            _, buffer = cv2.imencode(".jpg", resized, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                            
                            try:
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.connect(("127.0.0.1", 9999))
                                size = struct.pack(">L", len(buffer))
                                sock.sendall(size + buffer.tobytes())
                                sock.close()
                                print("📨 Alerta enviada al bot")
                            except Exception as e:
                                print(f"⚠️ No se pudo enviar alerta: {e}")
                            
                            self.counter_arms = 0
                            self.counter_helmet = 0
                    except Exception as e:
                        print(f"Detection error: {e}")
                
                # Calculate FPS
                elapsed = time.time() - start_time
                self.current_fps = 1.0 / elapsed if elapsed > 0 else 0
                
                # Add FPS and source info to frame
                cv2.putText(annotated_frame, f"FPS: {self.current_fps:.2f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                source_type = "FILE" if os.path.isfile(self.video_source) else "STREAM"
                cv2.putText(annotated_frame, f"Source: {source_type}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                # Encode frame with optimized quality
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
                ret, buffer = cv2.imencode('.jpg', annotated_frame, encode_param)
                if not ret:
                    continue
                    
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
            except Exception as e:
                print(f"⚠️ Frame processing error: {e}")
                continue

video_stream = VideoStream()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_stream', methods=['POST'])
def start_stream():
    data = request.json
    source = data.get('source', '')
    
    if not source:
        return jsonify({'success': False, 'message': 'Video source is required'})
    
    success, message = video_stream.start_stream(source)
    return jsonify({'success': success, 'message': message})

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    video_stream.stop_stream()
    return jsonify({'success': True, 'message': 'Stream stopped'})

@app.route('/status')
def status():
    return jsonify({
        'is_running': video_stream.is_running,
        'status': video_stream.status,
        'fps': round(video_stream.current_fps, 2)
    })

@app.route('/video_feed')
def video_feed():
    return Response(video_stream.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    try:
        os.makedirs('templates', exist_ok=True)
    except:
        pass  # Ignore errors in production
    
    # Default video path
    default_video = "/Users/rishavkumarraman/Desktop/freelance/smartsecurity/video/showcase.mov"
    
    # HTML content - will be served directly or from file
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Security - Live Camera Monitoring</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --background: 224 71% 4%;
            --foreground: 213 31% 91%;
            --muted: 223 47% 11%;
            --muted-foreground: 215.4 16.3% 56.9%;
            --popover: 224 71% 4%;
            --popover-foreground: 215 20.2% 65.1%;
            --border: 216 34% 17%;
            --input: 216 34% 17%;
            --card: 224 71% 4%;
            --card-foreground: 213 31% 91%;
            --primary: 210 40% 98%;
            --primary-foreground: 222.2 47.4% 1.2%;
            --secondary: 222.2 47.4% 11.2%;
            --secondary-foreground: 210 40% 98%;
            --accent: 216 34% 17%;
            --accent-foreground: 210 40% 98%;
            --destructive: 0 63% 31%;
            --destructive-foreground: 210 40% 98%;
            --ring: 216 34% 17%;
            --radius: 0.5rem;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: hsl(var(--background));
            min-height: 100vh;
            padding: 0;
            color: hsl(var(--foreground));
            overflow-x: hidden;
            line-height: 1.5;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
        }
        
        /* Header */
        .header {
            background-color: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            padding: 32px;
            margin-bottom: 24px;
            text-align: center;
        }
        
        .header-content {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            flex-wrap: wrap;
        }
        
        .logo {
            font-size: 48px;
        }
        
        h1 {
            font-size: 2.25rem;
            font-weight: 700;
            color: hsl(var(--foreground));
            letter-spacing: -0.025em;
            margin: 0;
        }
        
        .subtitle {
            color: hsl(var(--muted-foreground));
            font-size: 0.875rem;
            font-weight: 400;
            margin-top: 4px;
        }
        
        /* Control Panel */
        .control-panel {
            background-color: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            padding: 24px;
            margin-bottom: 24px;
        }
        
        /* Tabs */
        .tabs {
            display: inline-flex;
            height: 40px;
            align-items: center;
            justify-content: center;
            border-radius: var(--radius);
            background-color: hsl(var(--muted));
            padding: 4px;
            margin-bottom: 24px;
            width: 100%;
        }
        
        .tab {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            border-radius: calc(var(--radius) - 4px);
            padding: 6px 12px;
            font-size: 0.875rem;
            font-weight: 500;
            background: transparent;
            color: hsl(var(--muted-foreground));
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            flex: 1;
        }
        
        .tab:hover {
            color: hsl(var(--foreground));
        }
        
        .tab.active {
            background-color: hsl(var(--background));
            color: hsl(var(--foreground));
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .info-box {
            background-color: hsl(var(--muted));
            border: 1px solid hsl(var(--border));
            color: hsl(var(--foreground));
            padding: 12px 16px;
            border-radius: var(--radius);
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 0.875rem;
        }
        
        .control-section {
            margin-bottom: 20px;
        }
        
        .control-section label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: hsl(var(--foreground));
            font-size: 0.875rem;
        }
        
        .input-group {
            display: flex;
            gap: 12px;
            align-items: stretch;
        }
        
        input[type="text"] {
            flex: 1;
            height: 40px;
            padding: 8px 12px;
            font-size: 0.875rem;
            background-color: hsl(var(--background));
            border: 1px solid hsl(var(--input));
            border-radius: var(--radius);
            color: hsl(var(--foreground));
            transition: all 0.2s;
            font-family: 'Inter', sans-serif;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: hsl(var(--ring));
            box-shadow: 0 0 0 2px hsl(var(--ring) / 0.2);
        }
        
        input[type="text"]::placeholder {
            color: hsl(var(--muted-foreground));
        }
        
        input[type="text"]:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* Buttons */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            border-radius: var(--radius);
            font-size: 0.875rem;
            font-weight: 500;
            height: 40px;
            padding: 8px 16px;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            font-family: 'Inter', sans-serif;
            gap: 8px;
        }
        
        .btn-start {
            background-color: hsl(var(--primary));
            color: hsl(var(--primary-foreground));
        }
        
        .btn-start:hover:not(:disabled) {
            background-color: hsl(var(--primary) / 0.9);
        }
        
        .btn-stop {
            background-color: hsl(var(--destructive));
            color: hsl(var(--destructive-foreground));
        }
        
        .btn-stop:hover:not(:disabled) {
            background-color: hsl(var(--destructive) / 0.9);
        }
        
        .btn-demo {
            background-color: hsl(var(--secondary));
            color: hsl(var(--secondary-foreground));
        }
        
        .btn-demo:hover:not(:disabled) {
            background-color: hsl(var(--secondary) / 0.8);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-group {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 20px;
        }
        
        /* Status Bar */
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 24px;
            background-color: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            margin-bottom: 24px;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 500;
            font-size: 0.875rem;
        }
        
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 9999px;
            background: hsl(var(--muted-foreground));
        }
        
        .status-indicator.active {
            background: #22c55e;
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }
        
        /* Video Container */
        .video-container {
            background-color: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            padding: 24px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 600px;
            position: relative;
            overflow: hidden;
        }
        
        .video-container.streaming {
            border-color: hsl(var(--primary));
        }
        
        #videoFeed {
            max-width: 100%;
            max-height: 700px;
            border-radius: calc(var(--radius) - 4px);
            display: none;
        }
        
        .placeholder {
            text-align: center;
            color: hsl(var(--muted-foreground));
            padding: 48px 32px;
        }
        
        .placeholder-icon {
            font-size: 64px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        .placeholder-text {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: hsl(var(--foreground));
        }
        
        .placeholder-subtext {
            font-size: 0.875rem;
        }
        
        /* Messages */
        .message {
            padding: 12px 16px;
            margin: 16px 0;
            border-radius: var(--radius);
            display: none;
            font-weight: 500;
            font-size: 0.875rem;
            border: 1px solid;
        }
        
        .message.success {
            background-color: hsl(142.1 76.2% 36.3% / 0.1);
            color: #22c55e;
            border-color: hsl(142.1 76.2% 36.3% / 0.3);
        }
        
        .message.error {
            background-color: hsl(var(--destructive) / 0.1);
            color: #ef4444;
            border-color: hsl(var(--destructive) / 0.3);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            h1 {
                font-size: 1.875rem;
            }
            .logo {
                font-size: 36px;
            }
            .input-group {
                flex-direction: column;
            }
            .status-bar {
                flex-direction: column;
                gap: 12px;
            }
            .btn-group {
                flex-direction: column;
            }
            .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <div class="logo">🎥</div>
                <div>
                    <h1>Smart Security</h1>
                    <p class="subtitle">Live Camera Monitoring System</p>
                </div>
            </div>
        </div>
        
        <div class="control-panel">
            <div class="info-box">
                <span>📡</span>
                <span>Enter your RTSP camera URL to start streaming</span>
            </div>
            <div class="control-section">
                <label for="rtspUrl">RTSP URL:</label>
                <div class="input-group">
                    <input type="text" id="rtspUrl" placeholder="rtsp://username:password@ip:port/stream" value="rtsp://127.0.0.1:8554/camera">
                    <button class="btn btn-start" id="startBtn" onclick="startStream()">▶ Start Stream</button>
                    <button class="btn btn-stop" id="stopBtn" onclick="stopStream()" disabled>⏹ Stop</button>
                </div>
            </div>
        </div>
        
        <div id="message" class="message"></div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator" id="statusIndicator"></div>
                <span id="statusText">Status: Ready</span>
            </div>
            <div class="status-item">
                <span id="fpsText">FPS: 0</span>
            </div>
        </div>
        
        <div class="video-container" id="videoContainer">
            <img id="videoFeed" src="" style="display: none;">
            <div id="placeholder" class="placeholder">
                <div class="placeholder-icon">🎬</div>
                <div class="placeholder-text">No Active Stream</div>
                <div class="placeholder-subtext">Enter an RTSP URL above and click start to begin streaming</div>
            </div>
        </div>
    </div>
    
    <script>
        let statusInterval;
        
        function showMessage(text, type) {
            const msg = document.getElementById('message');
            msg.textContent = text;
            msg.className = 'message ' + type;
            msg.style.display = 'block';
            setTimeout(() => msg.style.display = 'none', 5000);
        }
        
        async function startStream() {
            const source = document.getElementById('rtspUrl').value.trim();
            
            if (!source) {
                showMessage('Please enter a valid RTSP URL', 'error');
                return;
            }
            
            const response = await fetch('/start_stream', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({source: source})
            });
            
            const data = await response.json();
            if (data.success) {
                showMessage(data.message, 'success');
                document.getElementById('videoContainer').classList.add('streaming');
                document.getElementById('videoFeed').src = '/video_feed?' + new Date().getTime();
                document.getElementById('videoFeed').style.display = 'block';
                document.getElementById('placeholder').style.display = 'none';
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('rtspUrl').disabled = true;
                
                startStatusUpdates();
            } else {
                showMessage(data.message, 'error');
            }
        }
        
        async function stopStream() {
            const response = await fetch('/stop_stream', {method: 'POST'});
            const data = await response.json();
            
            showMessage(data.message, 'success');
            document.getElementById('videoContainer').classList.remove('streaming');
            document.getElementById('videoFeed').src = '';
            document.getElementById('videoFeed').style.display = 'none';
            document.getElementById('placeholder').style.display = 'block';
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('rtspUrl').disabled = false;
            
            stopStatusUpdates();
        }
        
        function startStatusUpdates() {
            statusInterval = setInterval(async () => {
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
                    
                    document.getElementById('statusText').textContent = 'Status: ' + data.status;
                    document.getElementById('fpsText').textContent = 'FPS: ' + data.fps;
                    
                    const indicator = document.getElementById('statusIndicator');
                    if (data.is_running) {
                        indicator.classList.add('active');
                    } else {
                        indicator.classList.remove('active');
                    }
                } catch (e) {
                    console.error('Status update failed:', e);
                }
            }, 1000);
        }
        
        function stopStatusUpdates() {
            if (statusInterval) {
                clearInterval(statusInterval);
            }
            document.getElementById('statusText').textContent = 'Status: Stopped';
            document.getElementById('fpsText').textContent = 'FPS: 0';
            document.getElementById('statusIndicator').classList.remove('active');
        }
    </script>
</body>
</html>'''
    
    # Try to write template file (may fail in production)
    try:
        with open('templates/index.html', 'w') as f:
            f.write(html_content)
    except:
        pass  # Ignore write errors in production environments
    
    # Get port from environment variable (for deployment) or use default
    port = int(os.environ.get('PORT', 8080))
    
    # Only show detailed info in development
    if os.environ.get('PORT') is None:
        print("\n" + "="*70)
        print("🚀 Smart Security Video Stream Server")
        print("="*70)
        print(f"📱 Open your browser: http://127.0.0.1:{port}")
        print(f"📹 Demo video ready: {default_video}")
        print("="*70)
        print("Features:")
        print("  ✅ Play video files (MP4, MOV, AVI, etc.)")
        print("  ✅ Connect to RTSP camera streams")
        print("  ✅ Real-time FPS monitoring")
        print("  ✅ Video loops automatically")
        print("="*70)
        print("\nPress Ctrl+C to stop the server\n")
        app.run(debug=True, host='0.0.0.0', port=port, threaded=True)
    else:
        # Production mode - use gunicorn
        print(f"Starting Smart Security on port {port}")
