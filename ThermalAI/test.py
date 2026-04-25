from ultralytics import YOLO
import cv2

# Load a small pre-trained model
model = YOLO('yolov8n.pt') 

# Start laptop webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # Run YOLO detection
    results = model(frame)

    # Plot results on the frame
    annotated_frame = results[0].plot()

    cv2.imshow("YOLO Installation Test", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()