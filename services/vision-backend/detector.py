import cv2
import face_recognition
import pickle
import os
from ultralytics import YOLO
import numpy as np

class VisionDetector:
    def __init__(self):
        # Load YOLOv8 model (will auto-download on first run)
        print("[INFO] Loading YOLOv8 model...")
        self.yolo_model = YOLO('yolov8n.pt')  # Change to yolov8m.pt for better accuracy
        
        # Face recognition setup
        self.face_encodings_path = "face_db/encodings.pkl"
        self.known_encodings = []
        self.known_names = []
        self.load_face_encodings()
        
    def load_face_encodings(self):
        """Load saved face encodings from pickle file"""
        if os.path.exists(self.face_encodings_path):
            with open(self.face_encodings_path, "rb") as f:
                data = pickle.load(f)
                self.known_encodings = data.get("encodings", [])
                self.known_names = data.get("names", [])
            print(f"[INFO] Loaded {len(self.known_encodings)} known faces")
        else:
            print("[INFO] No existing face database found")
    
    def save_face_encodings(self):
        """Save face encodings to pickle file"""
        os.makedirs("face_db", exist_ok=True)
        with open(self.face_encodings_path, "wb") as f:
            pickle.dump({
                "encodings": self.known_encodings,
                "names": self.known_names
            }, f)
        print("[INFO] Face encodings saved")
    
    def detect_objects(self, frame):
        """Detect objects using YOLOv8"""
        results = self.yolo_model(frame, verbose=False)[0]
        detected_objects = []
        
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            label = self.yolo_model.names[class_id]
            
            detected_objects.append({
                "label": label,
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2]
            })
            
            # Draw on frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", 
                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 255, 0), 2)
        
        return detected_objects, frame
    
    def detect_faces(self, frame):
        """Detect and recognize faces"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize for faster processing
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        
        # Detect faces
        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)
        
        detected_faces = []
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Scale back to original size
            top, right, bottom, left = [v * 4 for v in face_location]
            
            # Try to match with known faces
            name = "Unknown"
            if len(self.known_encodings) > 0:
                matches = face_recognition.compare_faces(
                    self.known_encodings, face_encoding, tolerance=0.5
                )
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_names[first_match_index]
            
            detected_faces.append({
                "name": name,
                "bbox": [left, top, right, bottom],
                "encoding": face_encoding  # For adding new faces
            })
            
            # Draw on frame
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        return detected_faces, frame
    
    def add_face(self, frame, name):
        """Add a new face to the database"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        if len(face_encodings) == 0:
            return False, "No face detected in frame"
        
        if len(face_encodings) > 1:
            return False, "Multiple faces detected. Please ensure only one face is visible"
        
        # Add the face
        self.known_encodings.append(face_encodings[0])
        self.known_names.append(name)
        self.save_face_encodings()
        
        return True, f"Successfully added {name}"
    
    def delete_face(self, name):
        """Delete a face from the database"""
        if name not in self.known_names:
            return False, f"No face found with name: {name}"
        
        # Remove all instances of this name
        indices_to_keep = [i for i, n in enumerate(self.known_names) if n != name]
        self.known_encodings = [self.known_encodings[i] for i in indices_to_keep]
        self.known_names = [self.known_names[i] for i in indices_to_keep]
        self.save_face_encodings()
        
        return True, f"Successfully deleted {name}"
    
    def list_known_faces(self):
        """Return list of all known faces"""
        return list(set(self.known_names))
