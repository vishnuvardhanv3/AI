import os
import cv2
import json
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, "models", "haarcascade_frontalface_default.xml")
DATA = os.path.join(ROOT, "data")
PEOPLE = os.path.join(ROOT, "database", "people.json")
SAMPLES = 40
CAMERA_INDEX = 0
sys.path.insert(0, os.path.join(ROOT, "src"))
from database import init_db, add_person


def load_people():
    if not os.path.exists(PEOPLE):
        return {}
    with open(PEOPLE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_people(people):
    with open(PEOPLE, "w", encoding="utf-8") as f:
        json.dump(people, f, indent=2)


def main():
    init_db()
    name = input("Enter person's name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    people = load_people()
    if name in people:
        print("That person is already registered.")
        return
    ids = [int(v["id"]) for v in people.values()]
    person_id = max(ids, default=0) + 1
    detector = cv2.CascadeClassifier(MODEL)
    if detector.empty():
        raise RuntimeError("Could not load Haar Cascade.")
    person_dir = os.path.join(DATA, str(person_id))
    os.makedirs(person_dir, exist_ok=True)
    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        raise RuntimeError("Could not open webcam.")
    print(f"Registering {name}. Look at the camera.")
    print("Move your head slightly so the dataset has varied samples.")
    count = 0
    while count < SAMPLES:
        ok, frame = camera.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.1, 6, minSize=(80, 80))
        if len(faces):
            x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
            face = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            count += 1
            cv2.imwrite(os.path.join(person_dir, f"{count}.jpg"), face)
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, f"Samples: {count}/{SAMPLES}",
                        (x, max(25,y-10)), cv2.FONT_HERSHEY_SIMPLEX,
                        .7, (0,255,0), 2)
        cv2.imshow("Register Face - Q to cancel", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    camera.release()
    cv2.destroyAllWindows()
    if count < 10:
        print("Not enough samples. Please register again.")
        return
    people[name] = {"id": person_id}
    save_people(people)
    add_person(person_id, name)
    print(f"Registered {name} with {count} samples.")
    print("Run train.py before starting recognition.")


if __name__ == "__main__":
    main()
