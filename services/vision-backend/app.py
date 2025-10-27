try:
	import importlib
	_dotenv = importlib.import_module("dotenv")
	load_dotenv = getattr(_dotenv, "load_dotenv")
except Exception:
	# python-dotenv is not installed; provide a no-op fallback so the app can run without it
	def load_dotenv(*args, **kwargs):
		return False

load_dotenv()

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import cv2
import base64
import numpy as np
import os
import threading
import time
from detector import VisionDetector
from tts_handler import TTSHandler
from stt_handler import STTHandler
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Initialize components
detector = VisionDetector()
tts = TTSHandler()
stt = STTHandler()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    print("[INFO] Gemini API configured")
else:
    gemini_model = None
    print("[WARN] Gemini API key not found")

# Camera state
camera_active = False
camera_thread = None
latest_frame = None
frame_lock = threading.Lock()

def camera_worker():
    """Background thread to capture frames"""
    global latest_frame, camera_active
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open camera")
        camera_active = False
        return
    
    print("[INFO] Camera started")
    
    while camera_active:
        ret, frame = cap.read()
        if ret:
            with frame_lock:
                latest_frame = frame.copy()
        time.sleep(0.033)  # ~30 FPS
    
    cap.release()
    print("[INFO] Camera stopped")

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    """Start camera capture"""
    global camera_active, camera_thread
    
    if camera_active:
        return jsonify({"status": "already_running"}), 200
    
    camera_active = True
    camera_thread = threading.Thread(target=camera_worker, daemon=True)
    camera_thread.start()
    
    return jsonify({"status": "started"}), 200

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    """Stop camera capture"""
    global camera_active
    
    camera_active = False
    if camera_thread:
        camera_thread.join(timeout=2)
    
    return jsonify({"status": "stopped"}), 200

@app.route('/api/camera/status', methods=['GET'])
def camera_status():
    """Get camera status"""
    return jsonify({"active": camera_active}), 200

@app.route('/api/detect', methods=['POST'])
def detect():
    """Run detection on current frame or uploaded image"""
    global latest_frame
    
    # Get frame from request or use latest camera frame
    if 'image' in request.files:
        # Image uploaded
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    elif latest_frame is not None:
        # Use camera frame
        with frame_lock:
            frame = latest_frame.copy()
    else:
        return jsonify({"error": "No frame available"}), 400
    
    # Detect objects and faces
    objects, frame = detector.detect_objects(frame)
    faces, frame = detector.detect_faces(frame)
    
    # Encode annotated frame
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return jsonify({
        "objects": objects,
        "faces": faces,
        "annotated_image": f"data:image/jpeg;base64,{img_base64}"
    }), 200

@app.route('/api/describe', methods=['POST'])
def describe_scene():
    """Generate natural language description using Gemini"""
    global latest_frame
    
    # Get detection results
    if latest_frame is None:
        return jsonify({"error": "No frame available"}), 400
    
    with frame_lock:
        frame = latest_frame.copy()
    
    # Detect
    objects, _ = detector.detect_objects(frame)
    faces, _ = detector.detect_faces(frame)
    
    # Build context
    object_list = ", ".join([obj["label"] for obj in objects]) if objects else "no objects"
    face_list = ", ".join([f["name"] for f in faces]) if faces else "no people"
    
    context = f"Objects detected: {object_list}. People detected: {face_list}."
    
    # Generate description
    if gemini_model:
        try:
            prompt = f"You are assisting a visually impaired person. {context} Describe what you see in one clear, helpful sentence."
            response = gemini_model.generate_content(prompt)
            description = response.text.strip()
        except Exception as e:
            description = f"I can see {object_list} and {face_list}."
            print(f"[GEMINI ERROR] {e}")
    else:
        description = f"I can see {object_list} and {face_list}."
    
    # Speak description
    tts.speak(description)
    
    return jsonify({
        "description": description,
        "objects": objects,
        "faces": faces
    }), 200

@app.route('/api/face/add', methods=['POST'])
def add_face():
    """Add a new face to database"""
    global latest_frame
    
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    if latest_frame is None:
        return jsonify({"error": "No frame available"}), 400
    
    with frame_lock:
        frame = latest_frame.copy()
    
    success, message = detector.add_face(frame, name)
    
    if success:
        tts.speak(f"Saved {name} successfully")
        return jsonify({"status": "success", "message": message}), 200
    else:
        tts.speak(message)
        return jsonify({"status": "error", "message": message}), 400

@app.route('/api/face/delete', methods=['POST'])
def delete_face():
    """Delete a face from database"""
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    success, message = detector.delete_face(name)
    
    if success:
        tts.speak(f"Deleted {name}")
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 400

@app.route('/api/face/list', methods=['GET'])
def list_faces():
    """List all known faces"""
    faces = detector.list_known_faces()
    return jsonify({"faces": faces}), 200

@app.route('/api/voice/listen', methods=['POST'])
def voice_listen():
    """Listen for voice command"""
    text = stt.listen(timeout=10)
    
    if not text:
        return jsonify({"status": "no_speech"}), 200
    
    # Process command
    response_text = process_voice_command(text)
    tts.speak(response_text)
    
    return jsonify({
        "status": "success",
        "text": text,
        "response": response_text
    }), 200

def process_voice_command(text):
    """Process voice commands"""
    text = text.lower()
    
    if "what do you see" in text or "describe" in text:
        # Trigger description
        result = describe_scene()
        return result[0].json.get("description", "I cannot see anything right now")
    
    elif "save person as" in text or "add person" in text:
        # Extract name
        if "save person as" in text:
            name = text.split("save person as")[-1].strip()
        else:
            name = text.split("add person")[-1].strip()
        
        if name:
            with frame_lock:
                frame = latest_frame.copy() if latest_frame is not None else None
            
            if frame is not None:
                success, message = detector.add_face(frame, name)
                return message
        return "Please say the person's name"
    
    elif "who is" in text or "who are" in text:
        # Identify people
        if latest_frame is None:
            return "Camera is not active"
        
        with frame_lock:
            frame = latest_frame.copy()
        
        faces, _ = detector.detect_faces(frame)
        if faces:
            names = [f["name"] for f in faces]
            return f"I can see {', '.join(names)}"
        else:
            return "I don't see any faces"
    
    elif "delete person" in text or "remove person" in text:
        name = text.split("person")[-1].strip()
        if name:
            success, message = detector.delete_face(name)
            return message
        return "Please say the person's name to delete"
    
    else:
        return "I didn't understand that command. Try saying 'what do you see' or 'save person as [name]'"

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "camera_active": camera_active,
        "gemini_available": gemini_model is not None
    }), 200

if __name__ == '__main__':
    print("="*60)
    print("Vision-Mate Backend Server")
    print("="*60)
    print("Starting on http://localhost:5001")
    print("Endpoints:")
    print("  POST /api/camera/start    - Start camera")
    print("  POST /api/camera/stop     - Stop camera")
    print("  POST /api/detect          - Run detection")
    print("  POST /api/describe        - Describe scene with voice")
    print("  POST /api/face/add        - Add face (body: {name})")
    print("  POST /api/face/delete     - Delete face (body: {name})")
    print("  GET  /api/face/list       - List known faces")
    print("  POST /api/voice/listen    - Listen for voice command")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
