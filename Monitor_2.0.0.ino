const int analogInputPin = A0; // Analog input pin
const int samplingInterval = 2000; // Sampling interval in milliseconds (adjust as needed)

void setup() {
  pinMode(A0,INPUT);
  Serial.begin(115200); // Initialize serial communication
}

void loop() {
  unsigned long startTime = millis(); // Record the start time of the sampling interval
  int pulseCount = 1; // Initialize pulse count

  // Count pulses within the sampling interval
  while (millis() - startTime < samplingInterval) {
    if (analogRead(analogInputPin) > 700) { // Check if signal is above threshold (adjust threshold as needed)
      pulseCount++;
      while (analogRead(analogInputPin) > 700) {} // Wait until signal falls below threshold to count next pulse
    }
  }

  // Calculate frequency
  float frequency = pulseCount/ (samplingInterval / 1000.0); // Convert pulse count to frequency (Hz)

  // Output frequency to serial port
  
  Serial.println(frequency);
  
}
