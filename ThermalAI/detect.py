import cv2
from ultralytics import YOLO
import numpy as np
import time

# --- 1. Load Engine ---
model = YOLO('yolov8n.pt') 

def ai_structure_analyzer(roi):
    """
    Simulates a secondary AI check for physical structural integrity.
    In a real commercial app, this would be a second YOLO model trained 
    on 'Cracks', 'Missing Pins', or 'Surface Scratches'.
    """
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edge_density = np.sum(edges == 255) / (roi.shape[0] * roi.shape[1])
    
    # If edge density is unusually high, it suggests structural cracks/defects
    if edge_density > 0.15: 
        return "STRUCTURAL DEFECT"
    return "STRUCTURE WELL"

def classify_condition(frame_roi):
    hsv_roi = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2HSV)
    lower_hot = np.array([10, 100, 100]) 
    upper_hot = np.array([30, 255, 255])
    
    hot_mask = cv2.inRange(hsv_roi, lower_hot, upper_hot)
    total_area = frame_roi.shape[0] * frame_roi.shape[1]
    
    if total_area == 0: return "PENDING", 0, 0

    hot_pixel_count = cv2.countNonZero(hot_mask)
    spread = (hot_pixel_count / total_area) * 100
    
    # --- Thermal Stress Calculation ---
    # Stress increases as spread increases (Unit: MPa for simulation)
    thermal_stress = spread * 1.5 
    
    if spread > 40.0:
        return "DAMAGE", spread, thermal_stress
    elif spread < 10.0 and hot_pixel_count > 0:
        return "GOOD CONDITION", spread, thermal_stress
    else:
        return "STRESSED", spread, thermal_stress

def start_detection():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # Increased resolution for dual screen
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print("--- Reliability Guard AI Analyzer Active ---")
    print("LOGGING START: " + time.strftime("%Y-%m-%d %H:%M:%S"))

    while True:
        ret, frame = cap.read()
        if not ret: break

        results = model(frame, stream=True, conf=0.6, verbose=False) 
        
        # Main Visual: Vibrant Thermal Map
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        output_frame = cv2.applyColorMap(gray_frame, cv2.COLORMAP_JET)
        
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                roi = frame[y1:y2, x1:x2]
                if roi.size == 0: continue
                
                # 1. Thermal Analysis
                status, spread, stress = classify_condition(roi)
                
                # 2. AI Structural Analysis
                structure = ai_structure_analyzer(roi)
                
                # Dynamic Colors
                status_color = (0, 255, 0) if status == "GOOD CONDITION" else (0, 0, 255)
                struct_color = (0, 255, 0) if structure == "STRUCTURE WELL" else (0, 165, 255)

                # --- Terminal Reporting ---
                print(f"[RELIABILITY REPORT] Status: {status} | Stress: {stress:.2f}MPa | Structure: {structure}")

                # --- Dashboard Overlays ---
                # A. Main Bounding Box
                cv2.rectangle(output_frame, (x1, y1), (x2, y2), status_color, 2)
                cv2.putText(output_frame, f"{status} (Stress: {stress:.1f}MPa)", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

                # B. Dual-Side Display (The "Small Screen")
                # Creating a black info panel on the right side
                overlay = output_frame.copy()
                cv2.rectangle(output_frame, (950, 50), (1250, 350), (0,0,0), -1)
                cv2.addWeighted(overlay, 0.3, output_frame, 0.7, 0, output_frame)
                
                # C. Secondary Analysis Screen (Inside the panel)
                small_roi = cv2.resize(roi, (280, 180))
                plasma_roi = cv2.applyColorMap(cv2.cvtColor(small_roi, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_PLASMA)
                output_frame[60:240, 960:1240] = plasma_roi
                
                # D. Detailed Stats on Dashboard
                cv2.putText(output_frame, "ANALYSER STATES", (960, 260), 1, 1.2, (255,255,255), 2)
                cv2.putText(output_frame, f"Structure: {structure}", (960, 290), 1, 1, struct_color, 1)
                cv2.putText(output_frame, f"Heat Spread: {spread:.1f}%", (960, 315), 1, 1, (255,255,255), 1)
                cv2.putText(output_frame, f"Calculated Stress: {stress:.1f} MPa", (960, 340), 1, 1, (255,255,255), 1)

        cv2.imshow('Corporate Thermal Monitor v2.0', output_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            print("--- LOGGING ENDED BY USER ---")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_detection()