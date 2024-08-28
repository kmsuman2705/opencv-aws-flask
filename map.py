import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from geopy.geocoders import Nominatim
from datetime import datetime

# Function to get the current location (latitude, longitude)
def get_location():
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode("New Delhi, India")  # Specify your location or use a method to detect it
        return location.latitude, location.longitude, location.address.split(", ")[0], location.address.split(", ")[-1]
    except Exception as e:
        st.error(f"Error fetching location: {e}")
        return None, None, None, None

# Function to overlay text on image
def overlay_text_on_image(image, text, position, font_size=30, color=(255, 255, 255)):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)
    font = ImageFont.truetype("arial.ttf", font_size)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

# Function to overlay map on image
def overlay_map_on_image(image, lat, lon):
    # Get map image from static map API
    map_url = f"http://maps.google.com/maps/api/staticmap?center={lat},{lon}&zoom=14&size=300x300&sensor=false"
    response = requests.get(map_url)
    map_image = Image.open(BytesIO(response.content))

    # Convert to OpenCV format and resize map image
    map_image = map_image.resize((150, 150))
    map_image = cv2.cvtColor(np.array(map_image), cv2.COLOR_RGB2BGR)

    # Overlay map on top-right corner of the image
    h, w, _ = map_image.shape
    image[10:10+h, -10-w:-10] = map_image
    return image

# Streamlit UI setup
st.title("Webcam Capture with GPS Location & Timestamp")

# IP camera stream URL
video_url = 'http://192.168.137.127:8080/video'  # Replace with your camera's IP URL

# Open the video stream from the IP camera
video_capture = cv2.VideoCapture(video_url)

if not video_capture.isOpened():
    st.error("Error: Could not open video stream")
else:
    st.text("Video stream opened successfully")

# Create a placeholder to display the video
frame_placeholder = st.empty()

while True:
    ret, frame = video_capture.read()
    if not ret:
        st.error("Failed to capture video")
        break

    # Get GPS location
    lat, lon, city, country = get_location()
    if lat is not None and lon is not None:
        # Overlay map on image
        frame = overlay_map_on_image(frame, lat, lon)

        # Overlay timestamp and location text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        location_text = f"{city}, {country} (Lat: {lat}, Lon: {lon})"
        frame = overlay_text_on_image(frame, timestamp, (10, 10))
        frame = overlay_text_on_image(frame, location_text, (10, 50))

    # Display the frame with overlays
    frame_placeholder.image(frame, channels="BGR")

    # Break loop with 'Stop' button
    if st.button('Stop'):
        break

# Release the video capture object and close windows
video_capture.release()
cv2.destroyAllWindows()
