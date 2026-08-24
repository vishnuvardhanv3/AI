import os
import cv2
import json
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, "models", "haarcascade_frontalface_default.xml")
PEOPLE = os.path.join(ROOT, "database", "people.json")
FACE_MODEL = os.path.join(ROOT, "database", "face_model.yml")
CAMERA_INDEX = 0
UNKNOWN_THRESHOLD = 70.0
LOG_COOLDOWN_SECONDS = 5.0
ATTENDANCE_COOLDOWN_SECONDS = 15.0
sys.path.insert(0, os.path.join(ROOT, "src"))
from database import init_db, mark_attendance, log_access


def main():
    init_db()
    if not os.path.exists(FACE_MODEL):
        raise RuntimeError("No trained model. Run register.py and train.py first.")
    with open(PEOPLE, "r", encoding="utf-8") as f:
        people = json.load(f)
    id_to_name = {int(v["id"]): name for name, v in people.items()}
    detector = cv2.CascadeClassifier(MODEL)
    if detector.empty():
        raise RuntimeError("Could not load Haar Cascade.")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(FACE_MODEL)
    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        raise RuntimeError("Could not open webcam.")
    last_log, last_attendance = {}, {}
    previous = None
    smoothing = 0.65
    print("LIVE FACE SECURITY SYSTEM")
    print("Green = recognized / access granted")
    print("Red = unknown / access denied")
    print("Press Q to quit.")
    while True:
        ok, frame = camera.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=6, minSize=(80,80))
        for face_box in faces:
            x,y,w,h = map(int, face_box)
            if previous is not None:
                px,py,pw,ph = previous
                x = int(px*smoothing + x*(1-smoothing))
                y = int(py*smoothing + y*(1-smoothing))
                w = int(pw*smoothing + w*(1-smoothing))
                h = int(ph*smoothing + h*(1-smoothing))
            previous = (x,y,w,h)
            roi = gray[y:y+h, x:x+w]
            if roi.size == 0:
                continue
            roi = cv2.resize(roi,(200,200))
            predicted, distance = recognizer.predict(roi)
            now = time.time()
            if predicted in id_to_name and distance <= UNKNOWN_THRESHOLD:
                name = id_to_name[predicted]
                color = (0,255,0)
                status = "ACCESS GRANTED"
                if now - last_attendance.get(name, 0) >= ATTENDANCE_COOLDOWN_SECONDS:
                    mark_attendance(predicted, name)
                    last_attendance[name] = now
                if now - last_log.get(name, 0) >= LOG_COOLDOWN_SECONDS:
                    log_access(name, "GRANTED", distance)
                    last_log[name] = now
            else:
                name = "Unknown"
                color = (0,0,255)
                status = "ACCESS DENIED"
                if now - last_log.get("Unknown", 0) >= LOG_COOLDOWN_SECONDS:
                    log_access("Unknown", "DENIED", distance)
                    last_log["Unknown"] = now
            cv2.rectangle(frame,(x,y),(x+w,y+h),color,3)
            cv2.putText(frame,f"{name} | {distance:.1f}",(x,max(28,y-12)),
                        cv2.FONT_HERSHEY_SIMPLEX,.65,color,2,cv2.LINE_AA)
            cv2.putText(frame,status,(x,min(frame.shape[0]-10,y+h+28)),
                        cv2.FONT_HERSHEY_SIMPLEX,.62,color,2,cv2.LINE_AA)
        if len(faces) == 0:
            previous = None
        cv2.putText(frame,"LIVE FACE SECURITY",(20,35),
                    cv2.FONT_HERSHEY_SIMPLEX,.75,(255,255,255),2)
        cv2.putText(frame,f"Faces: {len(faces)}",(20,68),
                    cv2.FONT_HERSHEY_SIMPLEX,.65,(255,255,255),2)
        cv2.imshow("Face Recognition + Access Control",frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
