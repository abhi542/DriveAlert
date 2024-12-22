
import tkinter as tk
import customtkinter as ctk 
import torch
import numpy as np
import cv2
from PIL import Image, ImageTk
import vlc 
import random

# Initialize the app
app = tk.Tk()
app.geometry("800x800")
app.title("Drowsiness Detection and Alarming")
ctk.set_appearance_mode("dark")

# Create video frame and label
vidFrame = tk.Frame(app, height=480, width=600)
vidFrame.pack()
vid = ctk.CTkLabel(master=vidFrame, text="")  # Remove any default text
vid.pack()

# Initialize the counter
counter = 0
counterLabel = ctk.CTkLabel(
    master=app, 
    text=f"Counter: {str(counter)}", 
    height=40, 
    width=200, 
    font=("Arial", 20), 
    text_color="white", 
    fg_color="teal"
)
counterLabel.pack(pady=10)  # Position it outside the video frame

# Function to reset the counter
def reset_counter(): 
    global counter
    counter = 0 
    counterLabel.configure(text=f"Counter: {str(counter)}")

# Reset button
resetButton = ctk.CTkButton(
    master=app, 
    text="Reset Counter", 
    command=reset_counter, 
    height=40, 
    width=120, 
    font=("Arial", 20), 
    text_color="white", 
    fg_color="teal"
)
resetButton.pack()

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/runs/train/exp9/weights/last.pt', force_reload=True)

# Try opening the camera (index 0, 1, 2, etc.)
cap = cv2.VideoCapture(0)  # Try 0, 1, 2, or 3

if not cap.isOpened():
    print("Error: Camera not accessible.")
    exit()  # Exit if the camera cannot be accessed
else:
    print("Camera successfully opened.")

# Detection function
def detect(): 
    global counter
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        return  # Exit if frame capture fails

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
    results = model(frame)  # Run the YOLO model
    img = np.squeeze(results.render())  # Render the result image

    if len(results.xywh[0]) > 0:
        dconf = results.xywh[0][0][4]  # Confidence
        dclass = results.xywh[0][0][5]  # Class (1 is person)

        if dconf.item() > 0.80 and dclass.item() == 1.0:
            filechoice = random.choice([1,2,3])  # Random sound file
            filepath = f"{filechoice}.wav"  # Adjust path if files are in a subfolder
            print(f"Attempting to play: {filepath}")
            
            # Play sound
            p = vlc.MediaPlayer(filepath)
            if p is None:
                print("Error: VLC player initialization failed.")
            else:
                p.audio_set_volume(100)  # Ensure volume is set
                p.play()

            counter += 1  # Increment counter

    # Convert numpy image to PIL and then to Tkinter format
    imgarr = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(imgarr)
    vid.imgtk = imgtk
    vid.configure(image=imgtk)

    # Update counter label
    counterLabel.configure(text=f"Counter: {str(counter)}")

    # Continuously call the detect function
    vid.after(10, detect)

# Start detection
detect()

# Run main Tkinter loop
app.mainloop()