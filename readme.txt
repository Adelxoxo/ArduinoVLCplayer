Turn your Arduino into a real-time video player using VLC with the SSD1306 128x64px OLED display.
----------
You will need:
-an Arduino ATmega32 MCU
-an SSD1306 OLED display
-a computer to connect the Arduino to
----------
HARDWARE SETUP:
Connect the SSD1306 display to your Arduino, as such:
VCC -> 5V
GND -> GND
SCL -> A5
SDA -> A4
----------
PREREQUISITES:
pyserial
opencv-python
python-vlc
numpy
scikit-image
----------
To play videos:
-Connect the Arduino to your computer and upload the code to it.
-Open PlayerScript.py in a text editor and change the file path to that of your desired video (line 80)
-You may also need to change the COM port number (line 71)
-Save, run, and enjoy!
----------
NOTE:
This is a for-fun project, the video playback is ~7.05 FPS due to the limitations of the Arduino's 16MHz processor and the data streaming process.
VLC is not actually necessary to stream video to the Arduino at this rate - however, without it the playback will not be in real-time.
In short, the code works like this:
-starts VLC; 
-fetches, sends and displays the frame; waits for confirmation that the frame was successfully displayed; repeat until no frames remain.
Without VLC it would pull each frame one after another and display all of them, painstakingly at 1.4 seconds per frame.

Within PlayerScript.py there is a method for proper resolution scaling which I've left commented because the SSD1306's resolution is so tiny
that I feel the image loses the small amount of fidelity it has, if the distortion bothers you - simply uncomment lines 40-68, 90-91, and line 102.

Ideas to try out:
-add dithering
-rework the rendering method to be faster
-just buy an SD card module and avoid streaming entirely so you can have 30FPS playback and a slightly less terrible experience.

Have fun rewatching your favorite anime in the worst way imaginable!

-Adel