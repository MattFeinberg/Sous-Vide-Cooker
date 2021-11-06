#Remember correct pins for thermocouple
#Any time it uses the sousVide on/off pin it should be changed to connection to the smart plug
#I used an led to test it for now
#Account for extra stuff like changing time or desired temp during count down
#The thermocouple pins associated with each are in the comment above its declaration
#The breadboard setup is just 4 buttons and the oled which you connect to gnd 3v3 d2 and d4 accordingly


import ssd1306
import math
from machine import Pin, I2C
from time import sleep
from max6675 import MAX6675
import network
import urequests
from umqttsimple import MQTTClient

#therm = MAX6675(cs=Pin(15), sck=Pin(2), so=Pin(4))
therm = MAX6675(Pin(15), Pin(2), Pin(4))

i2c = I2C(0, scl = Pin(22), sda = Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

#Two variables that determine the time initially and during heating
timeCounter = 0
desiredTime = 0

desiredTemp = 20
currentTemp = therm.read()

#Configuration of buttons/switches
upSwitch = Pin(5, Pin.IN, Pin.PULL_UP) #Leftmost switch
downSwitch = Pin(23, Pin.IN, Pin.PULL_UP) #Middle switch
enter = Pin(27, Pin.IN, Pin.PULL_UP) #Rightmost switch
clear = Pin(33, Pin.IN, Pin.PULL_UP) #Right top switch

sousVide = Pin(19, Pin.OUT)

#Two variables that aid in the display of time in the format
#"minutes" : "seconds"
timeMin = 0
timeSec = 0

#This while loop displays the time desired based on how much you press
#the 15 and 30 second buttons
while enter.value() == 1:
    if desiredTime < 0:
        desiredTime = 0
    if upSwitch.value() == 0:
        desiredTime = desiredTime + 1
    if downSwitch.value() == 0:
        desiredTime = desiredTime - 1
    timeMin = math.floor(desiredTime / 60)
    timeSec = desiredTime % 60
    if timeSec < 10:
        display.fill(0)
        display.text("Time remaining: ", 5, 5)
        display.text(str(timeMin) + ":" + "0" + str(timeSec), 5, 15)
    else:
        display.fill(0)
        display.text("Time remaining: ", 5, 5)
        display.text(str(timeMin) + ":" + str(timeSec), 5, 15)
    display.text("Desired Temp: ", 5, 25)
    display.text("Current Temp:", 5, 45)
    if desiredTime > 1000 or clear.value() == 0:
        desiredTime = 0
    sleep(0.1)
    
sleep(1.5)

tempDisp = 20

#Need to determine an initial temp if we want one
#Also if we want it to be Celsius or Fahrenheit
while enter.value() == 1:
    if upSwitch.value() == 0:
        desiredTemp = desiredTemp + 1
    if downSwitch.value() == 0:
        desiredTemp = desiredTemp - 1
    tempDisp = desiredTemp
    if timeSec < 10:
        display.fill(0)
        display.text("Time remaining: ", 5, 5)
        display.text(str(timeMin) + ":" + "0" + str(timeSec), 5, 15)
    else:
        display.fill(0)
        display.text("Time remaining: ", 5, 5)
        display.text(str(timeMin) + ":" + str(timeSec), 5, 15)
    display.text("Desired Temp: ", 5, 25)
    display.text(str(tempDisp) + " C", 5, 35)
    display.text("Current Temp:", 5, 45)
    display.show()
    if clear.value() == 0:
        desiredTemp = 20
    if desiredTemp < 20 or desiredTemp > 120:
        desiredTemp = 20
    sleep(0.1)

sleep(1)

sousVide.on()
timeCounter = desiredTime

#This loop displays the time in minutes and seconds and counts down 
#every second

while timeCounter >= 0:
    currentTemp = therm.read()
    timeMin = math.floor(timeCounter / 60)
    timeSec = timeCounter % 60
    display.fill(0)
    if clear.value() == 0:
        timeCounter = -1
    if timeSec < 10:
        display.fill(0)
        display.text("Time remaining: ", 5, 5)
        display.text(str(timeMin) + ":" + "0" + str(timeSec), 5, 15)
        display.text("Desired Temp: ", 5, 25)
        display.text(str(tempDisp) + " C", 5, 35)
        display.text("Current Temp:", 5, 45)
        display.text(str(currentTemp),5, 55)
        display.show()
    else:
        display.fill(0)
        display.text("Time remaining: ", 5, 5)
        display.text(str(timeMin) + ":" + str(timeSec), 5, 15)
        display.text("Desired Temp: ", 5, 25)
        display.text(str(tempDisp) + " C", 5, 35)
        display.text("Current Temp:", 5, 45)
        display.text(str(currentTemp),5, 55)
        display.show()
    if currentTemp < desiredTemp:
        sousVide.on()
    elif currentTemp > desiredTemp:
        sousVide.off()
    sleep(1)

sousVide.off()
display.poweroff()