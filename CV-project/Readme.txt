Final deployed detector:
YOLO26s @ 640 fine-tuned on merged public + custom PCB short dataset

Primary deployment backend:
OpenVINO INT8 (CPU server)

Fallback:
PyTorch .pt

Class mapping:
0 = short

Inference threshold:
0.10

Tiled inference:
Enabled for larger/full-board images

Tile settings:
- tile size = 640
- overlap = 0.20
- tile merge IoU = 0.30

Warmup:
Model is loaded once at server startup and warmed with one dummy inference.

Output:
- highlighted image with boxes
- JSON-style detections: boxes + confidence