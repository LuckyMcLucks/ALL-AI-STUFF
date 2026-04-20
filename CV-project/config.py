from pathlib import Path

# Primary deployment model (CPU server)
MODEL_PATH = Path("best_openvino_model")   # quantized OpenVINO model folder

# Fallback model
FALLBACK_MODEL_PATH = Path("best.pt")

# Detection settings
CONF_THRES = 0.10
CLASS_ID = 0   # short

# Tiled inference settings
USE_TILED_INFERENCE = True
TILE_SIZE = 640
TILE_OVERLAP = 0.20
TILE_NMS_IOU = 0.30

# Visualization
BOX_COLOR = (0, 0, 255)   # red in BGR
BOX_THICKNESS = 2
FONT_SCALE = 0.6
FONT_THICKNESS = 2