from ultralytics import YOLO

model = YOLO("yolo11n.pt")

results = model.train(data="dataset.yaml", epochs=300, batch=16, imgsz=832)
