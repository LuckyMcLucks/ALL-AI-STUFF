import cv2
from fastapi import FastAPI, UploadFile, File
import fastapi
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
from PIL import Image
import io
from fastapi import FastAPI, UploadFile, File
import torch
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from detector import infer_pcb_image
app = FastAPI()
origins = [
    "http://localhost:3000",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, OPTIONS, etc.
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "working"}


def draw_boxes(image, boxes,conf,classes):
    for box in range(len(boxes)):
        x1, y1, x2, y2 = map(int, boxes[box])
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, f"conf:{conf[box]:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(image, f"class:{classes[box]}", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image
@app.post("/predict-image")
async def predict_image(file: UploadFile = File(...)):
    image_bytes = await file.read()

    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    results = infer_pcb_image(image, use_tiling=False, conf=0.01)
    print(results)
    # Draw bounding boxes   
    annotated = draw_boxes(image, results['boxes'],results['scores'],results['classes'])

    # Convert to image
    annotated_image = Image.fromarray(annotated)

    buf = io.BytesIO()
    results["visualized_image"].save(buf, format="JPEG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")