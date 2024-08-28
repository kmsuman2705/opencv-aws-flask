import streamlit as st
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

st.title('Real-Time Face Recognition and Alert System')

# Email configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = "sumankmishra99@gmail.com"
smtp_password = "gzox phoh kmlk eikc"
recipient_email = "kmsuman27@gmail.com"

# Directory configuration
known_faces_dir = r"C:\Users\LENOVO\Downloads\inueron_python\opencvprojectcollege\known"
unknown_faces_dir = r"C:\Users\LENOVO\Downloads\inueron_python\opencvprojectcollege\unknown"

# Initialize face recognition
known_face_encodings = []
known_face_names = []
captured_unknown_face_encodings = []

# Load known faces
for image_name in os.listdir(known_faces_dir):
    image_path = os.path.join(known_faces_dir, image_name)
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    
    if face_encodings:
        face_encoding = face_encodings[0]
        known_face_encodings.append(face_encoding)
        known_face_names.append(os.path.splitext(image_name)[0])

# Video stream URL
video_url = 'http://192.168.137.127:8080/video'
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
        st.error("Failed to grab frame")
        break
    
    # Convert the image from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find all the faces and face encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        else:
            name = "Unknown"
            if not any(face_recognition.compare_faces(captured_unknown_face_encodings, face_encoding, tolerance=0.6)):
                top, right, bottom, left = face_location
                face_image = frame[top:bottom, left:right]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unknown_image_path = os.path.join(unknown_faces_dir, f"unknown_{timestamp}.jpg")
                cv2.imwrite(unknown_image_path, face_image)

                captured_unknown_face_encodings.append(face_encoding)

                # Send email with the unknown face image
                msg = MIMEMultipart()
                msg['From'] = smtp_user
                msg['To'] = recipient_email
                msg['Subject'] = 'Unknown Face Detected'

                body = 'An unknown face has been detected and saved as an image.'
                msg.attach(MIMEText(body, 'plain'))

                with open(unknown_image_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename=unknown_{timestamp}.jpg')
                    msg.attach(part)

                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    text = msg.as_string()
                    server.sendmail(smtp_user, recipient_email, text)
                    st.success(f"Email sent with image {unknown_image_path}")
                except Exception as e:
                    st.error(f"Failed to send email: {e}")
                finally:
                    server.quit()

        # Draw a box around the face
        top, right, bottom, left = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Label the face with a name
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting frame
    frame_placeholder.image(rgb_frame, channels='RGB')

    # Exit the loop if the stream is closed
    if not cap.isOpened():
        break
