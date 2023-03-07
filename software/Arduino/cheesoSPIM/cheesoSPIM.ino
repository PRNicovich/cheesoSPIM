/*
Arduino sketch for cheesoSPIM

DSLR lens on SPI bus
rotational stepper on pins 4-7
laser TTL on laserPin with PWM power control

Communicates over serial
Corresponding Python device driver included with cheesoSPIM_GUI

*/

#include <SPI.h>
#include <Stepper.h>


unsigned int focusPosition = 800;
unsigned int focusMax = 1000;
unsigned int focusMin = 0;

const int rotationStep = 1;
const int rotationDir = 2;
const int stepsPerRevolution = 20;

Stepper rotStepper(20, 4, 5, 6, 7);

const int laserPin = 3; // Laser toggle pin
volatile byte laserPower = 128; // 0-255, analogWrite argument

volatile int motorMove = 0;

volatile unsigned int digitCount = 0;
String inputString = "";         // a string to hold incoming data
bool stringComplete = false;  // whether the string is complete

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial connection
  }

  //Serial.println("cheesoSPIM init");

  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  SPI.setClockDivider(SPI_CLOCK_DIV128);
  SPI.setDataMode(SPI_MODE3);

  //Serial.println("spi init");

  rotStepper.setSpeed(2000);

    //Serial.println("rot init");

  InitLens();

  //Serial.println("lens init");


  //Serial.println("init complete");
}



void loop() {

  //Going to deal with Serial here
  if (stringComplete) {
    
    char firstChar = char(inputString[0]);

    //Serial.println(firstChar);

    switch(firstChar) {

      case('D'):
        // Do demo motions of spin, lens, laser
        Serial.println("loop");
        // Lens goes in and out
        demoLens();
      
        // Steps in and out and spin to show off stage
        demoStage();
      
        // Lens goes to focus position
        setFocus();

        break; 
      
      case('E'):
        // Zoom lens in
        if (focusPosition != focusMax){
        focusPosition = focusPosition + 1;
        }
        else{
          focusPosition = focusMax;
        }
        setFocus();
        break;

      case('Q') :
        // Zoom lens out
        if (focusPosition != focusMin){
          focusPosition = focusPosition - 1;
        }
        else {
          focusPosition = focusMin;
        }
        setFocus();
        break;
        

      case('F') :
        // Set focus to XXXX where XXXX is 16-bit integer
        serialInputToLong(1);
        setFocus();
        break;

      case('N') :
        // Laser on
        analogWrite(laserPin, laserPower);
        break;

      case('O') :
        // Laser off
        analogWrite(laserPin, laserPower);
        break;

      case('I') :
        // Laser up
        laserPower = laserPower + 1;
        if (laserPower > 255){
          laserPower = 255;
        }
        analogWrite(laserPin, laserPower);
        break;

      case('K') : 
        // Laser down
        laserPower = laserPower - 1;
        if (laserPower < 0){
          laserPower = 0;
        }
        analogWrite(laserPin, laserPower);

        break;

      case('V'):
        // lens to close end position
        SPI.transfer(0x06); // Focus Min
        break;

      case('B'):
        // lens to far end position
        SPI.transfer(0x05); // Focus Max
        break;

      case('P') : 
        // Laser set
        serialInputToLong(2); // rest of input is power to set to
                              // nb - 0-255 is valid here. 
        analogWrite(laserPin, laserPower);
        break;

      case('L') : 
        // Rotate counter-clockwise, one step
        oneStep(true);
        break;

      case('R') : 
        // Rotate clockwise, one step
        oneStep(false);
        break;

      case('M') :
        serialInputToLong(3);
        rotStepper.step(motorMove);
        break;

      case('Y') :
        // Device ID
        Serial.println("cheesoSPIM");
        break;

      case('?'):
        // Query things
        switch(char(inputString[2])){
          case('L'):
            // laser power
            Serial.println(laserPower);
            break;

          case('F'):
            // Focus
            Serial.println(focusPosition);
            break;
            
        }

       default:
        Serial.println(15, HEX);
        break;
    }

    // Reset incoming serial
    inputString = "";
    stringComplete = false;
  }
  
}

void demoStage(){
  Serial.println("demo motors");
  rotStepper.step(1000);
  delay(500);
  rotStepper.step(-1000);
  delay(500);
}

void serialEvent() {

  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
      //Serial.println("Input:");
    /*  Serial.println(inputString);
      Serial.println("Size:");
      Serial.println(inputString.length()-1);
      */
    }
  }
}

void oneStep(bool dir){
  if (dir){
    rotStepper.step(1);
  }
  else{
    rotStepper.step(-1);
  }
}

void demoLens(){
  Serial.println("Demo lens");
  // Move lens in and out for a while
  delay(1000);
  SPI.transfer(0x05); // Focus Max
  delay(1000);
  SPI.transfer(0x06); // Focus min
  delay(1000);
}

void InitLens()
{
  SPI.transfer(0x0A);
  delay(30);
  SPI.transfer(0x00);
  delay(30);
  SPI.transfer(0x0A);
  delay(30);
  SPI.transfer(0x00);
  delay(30);
}

void setFocus() // Hoping this sets the position of the focus to middle.
{  
  SPI.transfer(0x44); // Relative move command
  delay(30);
  SPI.transfer(highByte(focusPosition));
  delay(30);
  SPI.transfer(lowByte(focusPosition));
  delay(30);
  SPI.transfer(0);
  delay(30);

}

void serialInputToLong(int setMode) {
        //Serial.println(inputString);
        long tempValue = 0;
        bool isNegNumber = false;
        digitCount = 0;
        for (int i = 2; i < inputString.length(); i++) {

          if ((inputString[i] >= 48) & (inputString[i] < 58)) {
            tempValue = tempValue*10;
            tempValue = tempValue + (inputString[i] - 48);
            //Serial.println(focusPosition);
            digitCount++;
          } // if is valid ascii numeral
          else if (inputString[i] == 45){
            // negative sign
            isNegNumber = true;
          }
        } // for loop over valid characters
  switch(setMode){
    case(1) :
      // Focus position
      if (isNegNumber){
        focusPosition = 65535 - tempValue;
      }
      else{
        focusPosition = tempValue;
      }
      //Serial.print("Focus = ");
      //Serial.println(focusPosition);
      break;

     case(2) :
      // laser power
      laserPower = tempValue;
      //Serial.print("Laser power = ");
      //Serial.println(laserPower);
      break;

      case(3):
        // motor move
        if (isNegNumber){
          motorMove = -tempValue;
        }
        else{
          motorMove = tempValue;
        }
        break;
  }
}
