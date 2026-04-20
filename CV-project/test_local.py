import cv2
from detector import infer_pcb_image

img = cv2.imread("my_board.jpg")
result = infer_pcb_image(img, use_tiling=True, conf=0.10)

print("Model used:", result["model_used"])
print("Detections:", result["num_detections"])
print("Boxes:", result["boxes"])
print("Scores:", result["scores"])

cv2.imwrite("output_detected.jpg", result["visualized_image"])
print("Saved output_detected.jpg")