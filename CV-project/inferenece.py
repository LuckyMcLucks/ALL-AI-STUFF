from fastapi import FastAPI, UploadFile, File
import fastapi
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
from PIL import Image
import io
from fastapi import FastAPI, UploadFile, File
import torch
from fastapi.middleware.cors import CORSMiddleware
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
model = YOLO('best.pt')
@app.get("/")
def root():
    return {"message": "working"}

@app.post("/predict-image")
async def predict_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    results = model(image)
    print(results)
    # Draw bounding boxes
    annotated = results[0].plot()

    # Convert to image
    annotated_image = Image.fromarray(annotated)

    buf = io.BytesIO()
    annotated_image.save(buf, format="JPEG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")