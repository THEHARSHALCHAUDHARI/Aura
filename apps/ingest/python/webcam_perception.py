import cv2
import torch
import numpy as np
import json
import os
from datetime import datetime
from facenet_pytorch import MTCNN, InceptionResnetV1

# ---------------- CONFIG ----------------
FACE_DB_DIR = "face_db"
EMB_PATH = f"{FACE_DB_DIR}/embeddings.npy"
NAME_PATH = f"{FACE_DB_DIR}/names.json"

DIST_THRESHOLD = 0.9
MOCK_LIDAR = 2.0

os.makedirs(FACE_DB_DIR, exist_ok=True)

# ---------------- LOAD MODELS ----------------
print("[INFO] Loading models...")

mtcnn = MTCNN(keep_all=True)
facenet = InceptionResnetV1(pretrained="vggface2").eval()

yolo = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
yolo.conf = 0.4

# ---------------- LOAD FACE DB ----------------
if os.path.exists(EMB_PATH) and os.path.getsize(EMB_PATH) > 0:
    try:
        embeddings = np.load(EMB_PATH)
        with open(NAME_PATH, "r") as f:
            names = json.load(f)
    except Exception:
        embeddings = np.empty((0, 512))
        names = []
else:
    embeddings = np.empty((0, 512))
    names = []

# ---------------- UTILS ----------------
def save_db():
    np.save(EMB_PATH, embeddings)
    with open(NAME_PATH, "w") as f:
        json.dump(names, f)

def recognize_face(emb):
    if len(embeddings) == 0:
        return "unknown"

    dists = np.linalg.norm(embeddings - emb, axis=1)
    min_idx = np.argmin(dists)

    if dists[min_idx] < DIST_THRESHOLD:
        return names[min_idx]
    return "unknown"

# ---------------- LOCATION PROVIDER ----------------
import gpsd
import geocoder

def get_gps_location():
    try:
        gpsd.connect()
        packet = gpsd.get_current()

        if packet.mode >= 2:
            return {
                "lat": packet.lat,
                "lng": packet.lon,
                "accuracy_m": packet.error.get("y", 10),
                "source": "gps"
            }
    except Exception:
        pass

    return None


def get_network_location():
    try:
        g = geocoder.ip("me")
        if g.ok and g.latlng:
            return {
                "lat": g.latlng[0],
                "lng": g.latlng[1],
                "accuracy_m": 5000,
                "source": "network"
            }
    except Exception:
        pass

    return None


def get_current_location():
    gps = get_gps_location()
    network = get_network_location()

    if gps:
        return {
            "primary": gps,
            "secondary": network
        }

    if network:
        return {
            "primary": network,
            "secondary": None
        }

    return None


  

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)

print("""
Aura Perception Console
-----------------------
[a] Add face
[d] Delete face
[q] Quit & save JSON
""")

scene_output = None

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # ---------- OBJECT DETECTION ----------
    yolo_results = yolo(frame)
    objects = []

    for *box, conf, cls in yolo_results.xyxy[0]:
        label = yolo.names[int(cls)]
        x1, y1, x2, y2 = map(int, box)
        objects.append((label, x1, y1, x2, y2))

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            label,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    # ---------- FACE DETECTION + EMBEDDINGS ----------
    boxes, probs = mtcnn.detect(frame)
    faces = mtcnn(frame)
    people = []

    if boxes is not None and faces is not None:
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)

            emb = facenet(faces[i].unsqueeze(0)).detach().numpy()[0]
            name = recognize_face(emb)

            people.append({
                "name": name,
                "distance_m": MOCK_LIDAR,
                "activity": "unknown"
            })

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(
                frame,
                name,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

    cv2.imshow("Aura Perception Console", frame)
    key = cv2.waitKey(1) & 0xFF

    # ---------- ADD FACE ----------
    if key == ord("a") and faces is not None:
        person_name = input("Enter name for this face: ").strip()
        if person_name:
            emb = facenet(faces[0].unsqueeze(0)).detach().numpy()[0]
            embeddings = np.vstack([embeddings, emb])
            names.append(person_name)
            save_db()
            print(f"[INFO] Added face: {person_name}")

    # ---------- DELETE FACE ----------
    if key == ord("d"):
        print("Known faces:", names)
        del_name = input("Enter name to delete: ").strip()
        if del_name in names:
            idx = names.index(del_name)
            embeddings = np.delete(embeddings, idx, axis=0)
            names.pop(idx)
            save_db()
            print(f"[INFO] Deleted face: {del_name}")

    # ---------- QUIT ----------
    if key == ord("q"):
        scene_output = {
            "timestamp": datetime.utcnow().isoformat(),
            "location": get_current_location(),
            "scene": "unknown",
            "people": people,
            "objects": [
                {"name": o[0], "distance_m": MOCK_LIDAR}
                for o in objects if o[0] != "person"
            ],
            "hazards": [],
            "image": "annotated_frame.jpg"
        }

        cv2.imwrite("annotated_frame.jpg", frame)
        break

cap.release()
cv2.destroyAllWindows()

# ---------------- SAVE JSON ----------------
with open("scene.json", "w") as f:
    json.dump(scene_output, f, indent=2)

print("\n=== FINAL AURA SCENE JSON ===")
print(json.dumps(scene_output, indent=2))
