from ultralytics import YOLO

# Load base model
model = YOLO("yolov8n.pt")

# Train model
model.train(
    data="dataset/data.yaml",
    epochs=50,
    imgsz=640
)