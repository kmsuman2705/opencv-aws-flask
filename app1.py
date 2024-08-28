import streamlit as st
import cv2
import numpy as np

st.title('OpenCV Streamlit App')

# URL of the external camera stream
video_url = 'http://10.244.62.27:8080/video'
cap = cv2.VideoCapture(video_url)

if not cap.isOpened():
    st.error("Error: Could not open video stream")
else:
    st.text("Video stream opened successfully")

# Create a placeholder to display the video
frame_placeholder = st.empty()

while True:
    ret, frame = cap.read()
    if not ret:
        st.text("Failed to grab frame")
        break
    
    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Display the frame
    frame_placeholder.image(frame_rgb, channels='RGB')
