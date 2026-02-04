import sys, json, cv2, torch, requests
import numpy as np
from datetime import datetime

image_url = sys.argv[1]
lidar_distance = float(sys.argv[2])

# Load image
resp = requests.get(image_url)
frame = cv2.imdecode(np.frombuffer(resp.content, np.uint8), cv2.IMREAD_COLOR)

# YOLO
model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
results = model(frame)

objects = []
for *box, conf, cls in results.xyxy[0]:
    x1,y1,x2,y2 = map(int, box)
    label = model.names[int(cls)]
    objects.append({
        "name": label,
        "distance_m": lidar_distance
    })

cv2.imwrite("annotated_frame.jpg", np.squeeze(results.render()))

scene = {
  "timestamp": datetime.utcnow().isoformat(),
  "scene": "workspace",
  "people": [o for o in objects if o["name"] == "person"],
  "objects": [o for o in objects if o["name"] != "person"],
  "hazards": [],
  "image": "annotated_frame.jpg"
}

print(json.dumps(scene))
