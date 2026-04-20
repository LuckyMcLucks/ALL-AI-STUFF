import cv2
import numpy as np
from ultralytics import YOLO
from config import (
    MODEL_PATH,
    FALLBACK_MODEL_PATH,
    CONF_THRES,
    CLASS_ID,
    USE_TILED_INFERENCE,
    TILE_SIZE,
    TILE_OVERLAP,
    TILE_NMS_IOU,
    BOX_COLOR,
    BOX_THICKNESS,
    FONT_SCALE,
    FONT_THICKNESS,
)

# LOAD MODEL ONCE
if MODEL_PATH.exists():
    model = YOLO(str(MODEL_PATH))
    ACTIVE_MODEL = str(MODEL_PATH)
else:
    model = YOLO(str(FALLBACK_MODEL_PATH))
    ACTIVE_MODEL = str(FALLBACK_MODEL_PATH)

# Warmup
dummy = np.zeros((640, 640, 3), dtype=np.uint8)
_ = model.predict(dummy, conf=CONF_THRES, verbose=False)


# HELPERS
def box_iou_xyxy(a, b):
    xA = max(a[0], b[0])
    yA = max(a[1], b[1])
    xB = min(a[2], b[2])
    yB = min(a[3], b[3])

    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter = inter_w * inter_h

    areaA = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    areaB = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    union = areaA + areaB - inter

    return inter / union if union > 0 else 0.0


def nms_xyxy(boxes, scores, iou_thresh=0.3):
    if not boxes:
        return []

    idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    keep = []

    while idxs:
        cur = idxs.pop(0)
        keep.append(cur)
        idxs = [i for i in idxs if box_iou_xyxy(boxes[cur], boxes[i]) < iou_thresh]

    return keep


def generate_tiles(image, tile_size=640, overlap=0.2):
    h, w = image.shape[:2]
    stride = int(tile_size * (1 - overlap))
    tiles = []

    y = 0
    while y < h:
        x = 0
        while x < w:
            x2 = min(x + tile_size, w)
            y2 = min(y + tile_size, h)

            x1 = max(0, x2 - tile_size)
            y1 = max(0, y2 - tile_size)

            tile = image[y1:y2, x1:x2]
            tiles.append((tile, x1, y1))

            if x + tile_size >= w:
                break
            x += stride

        if y + tile_size >= h:
            break
        y += stride

    return tiles


def draw_boxes(image_bgr, boxes, scores=None):
    out = image_bgr.copy()
    for i, (x1, y1, x2, y2) in enumerate(boxes):
        cv2.rectangle(out, (x1, y1), (x2, y2), BOX_COLOR, BOX_THICKNESS)
        label = "short" if scores is None else f"short {scores[i]:.2f}"
        cv2.putText(
            out,
            label,
            (x1, max(20, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            FONT_SCALE,
            BOX_COLOR,
            FONT_THICKNESS,
        )
    return out


# INFERENCE MODES
def infer_direct(image_bgr, conf=CONF_THRES):
    results = model.predict(image_bgr, conf=conf, verbose=False)

    boxes, scores = [], []
    for r in results:
        if r.boxes is None:
            continue

        xyxy = r.boxes.xyxy.cpu().numpy()
        confs = r.boxes.conf.cpu().numpy()
        clss = r.boxes.cls.cpu().numpy()

        for b, s, c in zip(xyxy, confs, clss):
            if int(c) != CLASS_ID:
                continue
            boxes.append([int(v) for v in b])
            scores.append(float(s))

    return boxes, scores


def infer_tiled(image_bgr, conf=CONF_THRES):
    tiles = generate_tiles(image_bgr, tile_size=TILE_SIZE, overlap=TILE_OVERLAP)

    all_boxes, all_scores,all_classes = [], [], []
    for tile, xoff, yoff in tiles:
        results = model.predict(tile, conf=conf, verbose=False)

        for r in results:
            if r.boxes is None:
                continue

            xyxy = r.boxes.xyxy.cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()
            clss = r.boxes.cls.cpu().numpy()

            for b, s, c in zip(xyxy, confs, clss):
                if int(c) != CLASS_ID:
                    continue

                x1, y1, x2, y2 = b
                all_boxes.append([
                    int(x1 + xoff),
                    int(y1 + yoff),
                    int(x2 + xoff),
                    int(y2 + yoff),
                ])
                all_scores.append(float(s))
                all_classes.append(int(c))

    keep = nms_xyxy(all_boxes, all_scores, iou_thresh=TILE_NMS_IOU)
    final_boxes = [all_boxes[i] for i in keep]
    final_scores = [all_scores[i] for i in keep]
    final_classes = [all_classes[i] for i in keep]
    return final_boxes, final_scores,final_classes



# MAIN ENTRY POINT
def infer_pcb_image(image_bgr, use_tiling=USE_TILED_INFERENCE, conf=CONF_THRES):
    if use_tiling:
        boxes, scores,classes = infer_tiled(image_bgr, conf=conf)
    else:
        boxes, scores = infer_direct(image_bgr, conf=conf)

    vis = draw_boxes(image_bgr, boxes, scores)
    return {
        "boxes": boxes,
        "scores": scores,
        "classes": classes,
        "num_detections": len(boxes),
        "visualized_image": vis,
        "model_used": ACTIVE_MODEL,
        "used_tiling": use_tiling,
    }