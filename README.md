# Real-Time Kinematic Digital Twin

A distributed mechatronics vision pipeline that captures human motion via a standard webcam, extracts 3D spatial coordinates using a heavy neural network, and streams the kinematic data over a local UDP network to render a live 3D digital twin on a secondary display.

## Architecture
This project is split into two asynchronous modules communicating via UDP:
1. **The Vision Broadcaster:** Runs MediaPipe Pose (Complexity 2) to extract 33 3D joint landmarks and broadcasts them as serialized JSON over a local socket.
2. **The Render Engine:** A lightweight, non-blocking UDP receiver that ingests the kinematic stream and renders a dynamic 3D skeletal mesh using hardware-accelerated OpenGL.

## Prerequisites
Tested on Windows 11 with Python 3.10. It is highly recommended to use an isolated Conda environment.

```bash
# Note: MediaPipe must be downgraded to 0.10.14 to utilize the mp.solutions API
pip install mediapipe==0.10.14 opencv-python pyqtgraph PyQt5 PyOpenGL PyOpenGL_accelerate
```

## How to run : 
run the following scripts on two different instances of your terminal 

```bash
python vision_broadcaster.py
```

```bash
python digital_twin.py
```

## note: 
Ensure your webcam has a clear view of your upper body.
Left-click and drag inside the 3D Render Window to rotate the digital twin in real-time.
Scroll wheel to zoom.
Press q in the webcam window to safely close the broadcaster.
Also make sure you install the required dependencies before running the scripts 
