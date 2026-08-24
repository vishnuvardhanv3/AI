# Real-Time Face Recognition Security System

A college-project-ready system combining real-time webcam face detection, LBPH face recognition, green/red face boxes, access control, SQLite attendance, security logs, and a local dashboard.

## System flow

```text
Webcam -> Haar Cascade Face Detection -> Face Crop -> LBPH Recognition
       -> Known: Access Granted + Attendance
       -> Unknown: Access Denied + Security Log
       -> Dashboard
```

## Setup (Windows)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Register people

```bash
python src/register.py
```

Enter a name and look at the camera. Capture around 40 samples. Repeat for each person.

## Train

```bash
python src/train.py
```

This creates `database/face_model.yml`.

## Start live security system

```bash
python src/recognize.py
```

The camera remains open and recognition happens continuously, frame by frame. Recognized people get a green box, name, access granted status, and attendance entry. Unknown people get a red box, Unknown, access denied, and a security log entry. Press `Q` to quit.

## Dashboard

```bash
python src/dashboard.py
```

The dashboard shows registered people, today's attendance, recent access attempts, and recognition distance.

## One-command menu

```bash
python main.py
```

## Haar Cascade model

Place the official OpenCV file at:

`models/haarcascade_frontalface_default.xml`

Download from the official OpenCV repository:

https://github.com/opencv/opencv/raw/4.x/data/haarcascades/haarcascade_frontalface_default.xml

The XML is used only to locate faces. LBPH is used to recognize registered people.

## Important

LBPH returns a distance rather than a true probability. Lower distance means a closer match. `UNKNOWN_THRESHOLD = 70.0` is a starting value and should be tuned using your own camera and lighting.

Do not commit personal face images, `face_model.yml`, `face_security.db`, or `people.json` containing real names/data to a public repository.

## Privacy and security

This is an educational/local access-control project, not a replacement for Windows Hello or production biometric authentication. Use biometric data only with appropriate consent. Basic LBPH recognition can be vulnerable to spoofing; production systems should use stronger face embeddings and dedicated liveness/anti-spoofing methods.
