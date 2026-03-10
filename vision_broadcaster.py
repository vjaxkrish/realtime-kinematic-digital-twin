# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 20:15:13 2026

@author: vjaxk
"""

import cv2
import mediapipe as mp
import socket
import json

# Initialize the heaviest, most accurate MediaPipe Pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    model_complexity=2, # 0, 1, or 2 (2 is the most resource-intensive)
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Setup UDP Socket for Inter-Process Communication (IPC)
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Broadcasting 3D kinematics to UDP {UDP_IP}:{UDP_PORT}")

# Change to 1 or 2 if you are using an external USB webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: 
        break

    # Convert BGR to RGB for MediaPipe processing
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_world_landmarks:
        # Draw the 2D overlay on the webcam feed
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Extract 3D coordinates (x, y, z) for all 33 joints
        landmarks = []
        for lm in results.pose_world_landmarks.landmark:
            landmarks.append([lm.x, lm.y, lm.z])

        # Serialize to JSON and fire it over the UDP socket
        data = json.dumps(landmarks).encode('utf-8')
        sock.sendto(data, (UDP_IP, UDP_PORT))

    cv2.imshow("Screen 1: Vision Broadcaster", frame)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()