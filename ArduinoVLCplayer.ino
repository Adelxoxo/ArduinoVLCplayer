#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

// Create an SSD1306 object
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Buffer to hold a chunk of image data
byte imageData[256];  // Adjust size to match chunk size

// Variables to track the current row and column position
int currentRow = 0;
int currentCol = 0;

void setup() {
  // Initialize the display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }

  display.clearDisplay();
  display.display();

  // Initialize serial communication
  Serial.begin(1000000);
  Serial.println("Ready to receive images...");
}

void loop() {
  // Wait for incoming data
  while (Serial.available() > 0) {
    int bytesRead = Serial.readBytes(imageData, sizeof(imageData));

    // Write the received chunk to the display at the correct position
    writeChunkToDisplay(imageData, bytesRead);

    // Send confirmation byte for chunk received
    Serial.write(0x01);  // Acknowledge that chunk was received
  }

  // After all data has been processed, check if the image is complete
  if (currentRow >= SCREEN_HEIGHT) {
    currentRow = 0;
    currentCol = 0;
    display.display();  // Final display update after all rows are completed
    Serial.write(0x02);  // Image complete confirmation signal

    // Reset display for the next image
    display.clearDisplay();
  }
}

// Function to write a chunk of image data to the display at the current position
void writeChunkToDisplay(byte *data, int length) {
  int bytesPerRow = SCREEN_WIDTH / 8;  // 128 pixels wide, 8 pixels per byte

  for (int i = 0; i < length; i++) {
    int x = currentCol * 8;  // Each byte represents 8 pixels

    // Set the byte on the display buffer (8 pixels)
    for (int bit = 0; bit < 8; bit++) {
      if (data[i] & (1 << (7 - bit))) {
        display.drawPixel(x + bit, currentRow, WHITE);
      } else {
        display.drawPixel(x + bit, currentRow, BLACK);
      }
    }

    currentCol++;
    if (currentCol >= bytesPerRow) {
      currentCol = 0;
      currentRow++;
    }

    if (currentRow >= SCREEN_HEIGHT) {
      break;
    }
  }
}