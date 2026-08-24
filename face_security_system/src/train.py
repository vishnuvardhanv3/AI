import os
import cv2
import json
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PEOPLE = os.path.join(ROOT, "database", "people.json")
MODEL = os.path.join(ROOT, "database", "face_model.yml")


def main():
    if not os.path.exists(PEOPLE):
        raise RuntimeError("No registered people. Run register.py first.")
    with open(PEOPLE, "r", encoding="utf-8") as f:
        people = json.load(f)
    images, labels = [], []
    for name, info in people.items():
        pid = int(info["id"])
        folder = os.path.join(DATA, str(pid))
        if not os.path.isdir(folder):
            continue
        for file in os.listdir(folder):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image = cv2.imread(os.path.join(folder, file), cv2.IMREAD_GRAYSCALE)
                if image is not None:
                    images.append(cv2.resize(image, (200, 200)))
                    labels.append(pid)
    if not images:
        raise RuntimeError("No face images found.")
    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=1, neighbors=8, grid_x=8, grid_y=8
    )
    recognizer.train(images, np.array(labels, dtype=np.int32))
    recognizer.write(MODEL)
    print("Training complete.")
    print(f"Registered people: {len(people)}")
    print(f"Training images: {len(images)}")
    print(f"Model: {MODEL}")


if __name__ == "__main__":
    main()
