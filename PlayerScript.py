import os
import serial
import time
import cv2  # Import OpenCV for video handling
import vlc  # Import the VLC Python bindings
import numpy as np  # Import NumPy for array handling
from skimage.metrics import structural_similarity as ssim  # Import SSIM

# Define the screen dimensions
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

# Function to convert frame to monochrome byte array
def frame_to_monochrome_array(frame):
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)  # Convert to binary image
    img = cv2.resize(img, (SCREEN_WIDTH, SCREEN_HEIGHT), interpolation=cv2.INTER_NEAREST)

    data = bytearray()
    for y in range(SCREEN_HEIGHT):
        byte = 0
        for x in range(SCREEN_WIDTH):
            if img[y, x] == 255:  # Inverted logic, white becomes 0
                byte |= (1 << (7 - (x % 8)))
            if (x + 1) % 8 == 0:  # Every 8 pixels, add byte to data
                data.append(byte)
                byte = 0
        if SCREEN_WIDTH % 8 != 0:  # Add remaining bits if needed
            data.append(byte)

    return data

def get_current_frame(player):
    """Get the current frame from the VLC player."""
    player.video_take_snapshot(0, "current_frame.jpg", 0, 0)  # Take a snapshot
    frame = cv2.imread("current_frame.jpg")  # Read the snapshot as an image
    return frame

# FRAME SCALING
# def resize_frame(frame, video_width, video_height):
#     """Resize the frame according to the video's aspect ratio for a 128x64 display."""
#     target_aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
#     video_aspect_ratio = video_width / video_height

#     # Determine new dimensions to maintain aspect ratio
#     if video_aspect_ratio > target_aspect_ratio:
#         # Video is wider than display
#         new_width = SCREEN_WIDTH
#         new_height = int(SCREEN_WIDTH / video_aspect_ratio)
#     else:
#         # Video is taller than display
#         new_height = SCREEN_HEIGHT
#         new_width = int(SCREEN_HEIGHT * video_aspect_ratio)

#     # Resize the frame
#     frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

#     # Center the resized frame on a black background
#     top = (SCREEN_HEIGHT - new_height) // 2
#     bottom = SCREEN_HEIGHT - new_height - top
#     left = (SCREEN_WIDTH - new_width) // 2
#     right = SCREEN_WIDTH - new_width - left

#     # Create a new black frame and place the resized frame on it
#     new_frame = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
#     new_frame[top:top + new_height, left:left + new_width] = frame

#     return new_frame

def main():
    arduino = serial.Serial('COM5', 1000000) # Adjust if needed (you probably need to)
    arduino.timeout = 1  # Set timeout to prevent hanging
    time.sleep(2)  # Wait for the Arduino to initialize

    # Start VLC instance and get the current media player
    instance = vlc.Instance()
    player = instance.media_player_new()

    # Load and play a video in VLC
    video_path = r'C:\your_videos_file_path_goes_here.mp4'  # Video file path
    media = instance.media_new(video_path)
    player.set_media(media)
    player.play()

    # Wait for the player to start
    time.sleep(2)

    # FRAME SCALING
    # Get the video's dimensions
    #video_width = player.video_get_width()
    #video_height = player.video_get_height()

    while True:
        # Get the current frame from the VLC player
        frame = get_current_frame(player)
        if frame is None:
            print("Failed to capture frame.")
            continue

        print('Processing frame...')
        # FRAME SCALING
        #frame = resize_frame(frame, video_width, video_height)  # Resize frame based on aspect ratio
        frame_data = frame_to_monochrome_array(frame)

        print('Sending frame...')
        start_time = time.time()  # Record the start time

        # Send the frame data in chunks
        for i in range(0, len(frame_data), 256):
            chunk = frame_data[i:i + 256]
            arduino.write(chunk)

            # Wait for chunk confirmation
            response = arduino.read(1)  # Read a single byte
            while response != b'\x01':
                response = arduino.read(1)
                if not response:  # Break if no response
                    print("No response from Arduino, breaking.")
                    break

        # Wait for final confirmation from Arduino before moving to the next frame
        response = arduino.read(1)
        while response != b'\x02':
            response = arduino.read(1)
            if not response:  # Break if no response
                print("No final confirmation from Arduino, breaking.")
                break

        end_time = time.time()  # Record the end time
        display_time = end_time - start_time  # Calculate display time for this frame

        print(f"Frame displayed successfully in {display_time:.4f} seconds.")

        # Check if VLC is still playing
        if player.get_state() not in (vlc.State.Playing, vlc.State.Paused):
            print("Video playback has ended.")
            break

    # Cleanup
    arduino.close()
    player.stop()  # Stop VLC playback

if __name__ == "__main__":
    main()