import sys
import socket
import json
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph.opengl as gl

# Connect to the UDP Socket
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False) # Non-blocking so the GUI doesn't freeze

# Define the skeletal topology (which joint connects to which)
CONNECTIONS = [
    (11,12), (11,13), (13,15), (15,17), (15,19), (15,21), (17,19), # Left Arm
    (12,14), (14,16), (16,18), (16,20), (16,22), (18,20),          # Right Arm
    (11,23), (12,24), (23,24),                                     # Torso
    (23,25), (25,27), (27,29), (29,31), (27,31),                   # Left Leg
    (24,26), (26,28), (28,30), (30,32), (28,32),                   # Right Leg
    (0,1), (1,2), (2,3), (3,7), (0,4), (4,5), (5,6), (6,8)         # Face
]

# Initialize the High-Performance OpenGL Window
app = QtWidgets.QApplication(sys.argv)
w = gl.GLViewWidget()
w.opts['distance'] = 2.5
w.setWindowTitle('Screen 2: Real-Time 3D Digital Twin')
w.setGeometry(100, 100, 1000, 800)
w.show()

# Add a floor grid
grid = gl.GLGridItem()
grid.scale(2, 2, 2)
w.addItem(grid)

# Initialize scatter plot for joints and lines for bones
scatter = gl.GLScatterPlotItem(pos=np.zeros((33, 3)), color=(0, 1, 0, 1), size=12)
w.addItem(scatter)
lines = gl.GLLinePlotItem(pos=np.zeros((len(CONNECTIONS)*2, 3)), color=(0, 0.8, 1, 1), mode='lines', width=3)
w.addItem(lines)

def update():
    try:
        # Drain the UDP buffer to get the absolute latest frame
        while True:
            data, _ = sock.recvfrom(4096)
            
        # We purposely break out of the loop above when BlockingIOError is thrown,
        # but we handle the data in the except block below.
    except BlockingIOError:
        pass
        
    try:
        # Decode the JSON payload
        landmarks = json.loads(data.decode('utf-8'))
        
        # Convert to numpy array
        raw_pts = np.array(landmarks)
        pts = np.zeros_like(raw_pts)
        
        # Map MediaPipe axes to OpenGL 3D space (Stand the skeleton up)
        pts[:, 0] = raw_pts[:, 0]         # X stays X (Left/Right)
        pts[:, 1] = -raw_pts[:, 2]        # MediaPipe Z (Depth) becomes OpenGL Y (Forward/Back)
        pts[:, 2] = -raw_pts[:, 1]        # Inverted MediaPipe Y (Down) becomes OpenGL Z (Up)

        # Update joint positions in the OpenGL Engine
        scatter.setData(pos=pts)

        # Update bone segments
        bone_pts = []
        for p1, p2 in CONNECTIONS:
            bone_pts.append(pts[p1])
            bone_pts.append(pts[p2])
        lines.setData(pos=np.array(bone_pts))
        
    except NameError:
        pass # Handle startup before first packet arrives

# Set a hardware timer to pull frames at roughly 60 FPS
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(16)

if __name__ == '__main__':
    sys.exit(app.exec_())