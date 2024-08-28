import streamlit as st
import speech_recognition as sr
import smtplib
from email.mime.text import MIMEText

# Email configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = "sumankmishra99@gmail.com"  # Replace with your email
smtp_password = "gzox phoh kmlk eikc"  # Replace with your app password

# Email sending function
def send_email(recipient_email, subject, body):
    msg = MIMEText(body)
    msg['From'] = smtp_user
    msg['To'] = recipient_email
    msg['Subject'] = subject

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipient_email, msg.as_string())
        server.quit()
        st.success(f"Email sent to {recipient_email} with subject '{subject}'")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Streamlit UI
st.title("Voice-Activated Email Alert")

if st.button("Speak and Send Email"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Please speak now...")
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio).lower()
            st.write(f"You said: {command}")

            if "police" in command:
                send_email("kmsuman27@gmail.com", "Alert: Police Assistance Needed", "This is an automated message requesting police assistance.")
            elif "padosi" in command:
                send_email("avijitdutta8798@gmail.com", "Alert: Neighbor Assistance Needed", "This is an automated message requesting neighbor assistance.")
            else:
                st.warning("No valid command recognized. Please say 'police' or 'neighbor'.")
        
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
        except sr.RequestError:
            st.error("Could not request results from Google Speech Recognition service.")
