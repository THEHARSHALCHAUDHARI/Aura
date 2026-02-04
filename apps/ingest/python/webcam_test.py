import cv2
import torch
import json
from datetime import datetime

# ---------- LOAD MODELS ----------
print("[INFO] Loading YOLOv5...")
model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
model.conf = 0.4

# ---------- OPEN WEBCAM ----------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

print("[INFO] Press SPACE to capture frame, ESC to exit")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    cv2.imshow("Aura Webcam Preview", frame)
    key = cv2.waitKey(1)

    # SPACE = capture
    if key == 32:
        break
    # ESC = exit
    if key == 27:
        cap.release()
        cv2.destroyAllWindows()
        exit()

cap.release()
cv2.destroyAllWindows()

# ---------- OBJECT DETECTION ----------
results = model(frame)
detections = []

for *box, conf, cls in results.xyxy[0]:
    x1, y1, x2, y2 = map(int, box)
    label = model.names[int(cls)]

    detections.append({
        "name": label,
        "distance_m": 2.0  # mock LiDAR for now
    })

# ---------- SAVE ANNOTATED IMAGE ----------
annotated = results.render()[0]
cv2.imwrite("annotated_frame.jpg", annotated)

# ---------- BUILD SCENE JSON ----------
scene = {
    "timestamp": datetime.utcnow().isoformat(),
    "scene": "unknown",
    "people": [d for d in detections if d["name"] == "person"],
    "objects": [d for d in detections if d["name"] != "person"],
    "hazards": [],
    "image": "annotated_frame.jpg"
}

# ---------- OUTPUT ----------
with open("scene.json", "w") as f:
    json.dump(scene, f, indent=2)

print("\n=== AURA SCENE OUTPUT ===")
print(json.dumps(scene, indent=2))
print("\nSaved annotated_frame.jpg and scene.json")
