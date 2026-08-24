import subprocess
import sys

print("=" * 55)
print("     REAL-TIME FACE SECURITY SYSTEM")
print("=" * 55)
print("1. Register Person")
print("2. Train Face Recognition Model")
print("3. Start Live Recognition + Access Control")
print("4. Open Attendance / Security Dashboard")
print("5. Exit")

choice = input("\nChoose: ").strip()

commands = {
    "1": "src/register.py",
    "2": "src/train.py",
    "3": "src/recognize.py",
    "4": "src/dashboard.py",
}

if choice in commands:
    subprocess.run([sys.executable, commands[choice]])
elif choice == "5":
    print("Goodbye.")
else:
    print("Invalid choice.")
