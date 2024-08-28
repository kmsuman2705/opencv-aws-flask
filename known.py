import cv2
import face_recognition
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Initialize face recognition
known_face_encodings = []
known_face_names = []

# Store unknown face encodings to prevent multiple captures
captured_unknown_face_encodings = []

# Directory containing images of known persons
known_faces_dir = r"C:\Users\LENOVO\Downloads\inueron_python\opencvprojectcollege\known"

# Directory to save images of unknown persons
unknown_faces_dir = r"C:\Users\LENOVO\Downloads\inueron_python\opencvprojectcollege\unknown"

# Email configuration
smtp_server = "smtp.gmail.com"  # Replace with your SMTP server
smtp_port = 587  # Replace with your SMTP port
smtp_user = "sumankmishra99@gmail.com"  # Replace with your email
smtp_password = "gzox phoh kmlk eikc"  # Replace with your app password
recipient_email = "kmsuman27@gmail.com"  # Replace with the recipient's email

# Load each image file and extract face encodings
for image_name in os.listdir(known_faces_dir):
    image_path = os.path.join(known_faces_dir, image_name)
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    
    if face_encodings:
        face_encoding = face_encodings[0]
        known_face_encodings.append(face_encoding)
        known_face_names.append(os.path.splitext(image_name)[0])

# Initialize webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Convert the image from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find all the faces and face encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = face_distances.argmin()

        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        else:
            name = "Unknown"
            # Check if this unknown face has already been captured
            if not any(face_recognition.compare_faces(captured_unknown_face_encodings, face_encoding, tolerance=0.6)):
                # Save the unknown face image
                top, right, bottom, left = face_location
                face_image = frame[top:bottom, left:right]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unknown_image_path = os.path.join(unknown_faces_dir, f"unknown_{timestamp}.jpg")
                cv2.imwrite(unknown_image_path, face_image)

                # Add the unknown face encoding to the list
                captured_unknown_face_encodings.append(face_encoding)
                
                # Send the unknown face image via email
                msg = MIMEMultipart()
                msg['From'] = smtp_user
                msg['To'] = recipient_email
                msg['Subject'] = 'Unknown Face Detected'
                
                body = 'An unknown face has been detected and saved as an image.'
                msg.attach(MIMEText(body, 'plain'))
                
                attachment = open(unknown_image_path, 'rb')
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename=unknown_{timestamp}.jpg')
                msg.attach(part)
                
                # Send email
                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    text = msg.as_string()
                    server.sendmail(smtp_user, recipient_email, text)
                    print(f"Email sent with image {unknown_image_path}")
                except Exception as e:
                    print(f"Failed to send email: {e}")
                finally:
                    server.quit()
                    attachment.close()

        # Draw a box around the face
        top, right, bottom, left = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Label the face with a name
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
video_capture.release()
cv2.destroyAllWindows()