#Remember correct pins for thermocouple
#Any time it uses the sousVide on/off pin it should be changed to connection to the smart plug
#I used an led to test it for now
#The thermocouple pins associated with each are in the comment above its declaration
#The breadboard setup is just 4 capacitive touch tapes and the oled which you connect to gnd 3v3 d2 and d4 accordingly
#you press enter tape to start the oled/input time, you press switch tape to switch to inputting temperature, then you press enter to start the
#sousVide machine function. This is the only way I can get this to work but it do be making a lil sense!


import ssd1306, math
from machine import Pin, I2C, TouchPad
from time import sleep
from max6675 import MAX6675
import paho.mqtt.publish as publish

#Smart plug set up
MQTTSERVER = '192.168.86.24'
PLUG = 'ESPURNA-BF5B67'


#therm = MAX6675(cs=Pin(15), sck=Pin(2), so=Pin(4))
therm = MAX6675(Pin(15), Pin(2), Pin(4))

i2c = I2C(0, scl = Pin(22), sda = Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c)


#Configuration of capacitive touch tapes
upSwitch = TouchPad(Pin(13))             ##BLACK
downSwitch = TouchPad(Pin(14))           ##GREEN
enter =  TouchPad(Pin(27))               ##ORANGE
switch = TouchPad(Pin(33))               ##BLUE
clear = TouchPad(Pin(12))                ##BROWN 

sousVide = Pin(19, Pin.OUT)


#This while loop displays the time desired based on how much you press the buttons

def main():
    ### GET TIME AND TEMP FROM USER ###
    display.text("Time remaining:", 5, 5)
    display.text("Desired Temp: ", 5, 25)
    display.text("Current Temp:", 5, 45)
    display.show()
    sleep(.2)
    enterValue = enter.read()
    settingNums = True
    desiredTime = 0
    desiredTemp = 0
    currentTemp = therm.read()
    runTime = True
    ##Allow user to switch between setting time and temp
    while settingNums:
        if(runTime):
            results = setTime(desiredTime, desiredTemp, currentTemp)
            settingNums = results[0]
            desiredTime = results[1]
        else:
            results = setTemp(desiredTime, desiredTemp, currentTemp)
            settingNums = results[0]
            desiredTemp = results[1]
        runTime = not runTime
    print("pressed enter")
    print (str(desiredTemp))
    print(str(desiredTime))
    print("exit")
    ### BEGIN COOKING ###
    sousVideCook()
    
    ### OFF ###
    display.poweroff()
    return
    

#This function takes care of turning the machine on and off to cook the food.
def sousVideCook():
    global timeCounter, clearValue2
    sousVide.on()
    
    timeCounter = 0
    timeCounter = desiredTime
    
    while timeCounter >= 0:
        
        clearValue2 = clear.read()
        currentTemp = therm.read()
        timeHour = math.floor(timeCounter / 60)
        timeMin = timeCounter % 60
        display.fill(0)
        
        if clearValue2 < 200: #I set to 200, Rusny had it at 20 (I think a typo)
            timeCounter = -1
            break
        if timeMin < 10:
            display.fill(0)
            display.text("Time remaining: ", 5, 5)
            display.text(str(timeHour) + ":" + "0" + str(timeMin), 5, 15)
            display.text("Desired Temp: ", 5, 25)
            display.text(str(tempDisp) + " C", 5, 35)
            display.text("Current Temp:", 5, 45)
            display.text(str(currentTemp),5, 55)
            display.show()
        else:
            display.fill(0)
            display.text("Time remaining: ", 5, 5)
            display.text(str(timeHour) + ":" + str(timeMin), 5, 15)
            display.text("Desired Temp: ", 5, 25)
            display.text(str(tempDisp) + " C", 5, 35)
            display.text("Current Temp:", 5, 45)
            display.text(str(currentTemp),5, 55)
            display.show()
            if currentTemp < desiredTemp:
                sousVide.on()
            elif currentTemp > desiredTemp:
                sousVide.off()
            sleep(60)
            timeCounter -= 1
            
    sousVide.off()
    display.poweroff()

#Displays the numbers on the oled screen.
def displayNums(desiredTime, desiredTemp, currentTemp):
    display.fill(0)
    timeHour = math.floor(desiredTime / 60)
    timeMin = desiredTime % 60
    display.text("Time remaining:", 5, 5)
    display.text("Desired Temp: ", 5, 25)
    display.text("Current Temp:", 5, 45)
    if timeMin < 10:
        display.text(str(timeHour) + ":" + "0" + str(timeMin), 5, 15)#"Hours" : "minutes" : "seconds"
    else:
        display.text(str(timeHour) + ":" + str(timeMin), 5, 15)
    display.text("Desired Temp: ", 5, 25)
    display.text(str(desiredTemp) + " C", 5, 35)
    display.text("Current Temp:", 5, 45)
    display.text(str(currentTemp),5, 55)
    display.show()

def setTime(desiredTime, desiredTemp, currentTemp):
    enterValue = enter.read()
    switchValue = switch.read()
    while (switchValue > 200 and enterValue > 200):
        up = upSwitch.read()
        down = downSwitch.read()
        clearValue = clear.read()
        if up < 200:
            desiredTime += 1
            displayNums(desiredTime, desiredTemp, currentTemp)
            sleep(.4)
            up = upSwitch.read()
            while (up < 200):
                desiredTime += 1
                displayNums(desiredTime, desiredTemp, currentTemp)
                sleep(.1)
                up = upSwitch.read()
        elif down < 200:
            desiredTime -= 1
            displayNums(desiredTime, desiredTemp, currentTemp)
            sleep(.4)
            down = downSwitch.read()
            while (down < 200):
                desiredTime -= 1
                displayNums(desiredTime, desiredTemp, currentTemp)
                sleep(.1)
                down = downSwitch.read()
        if clearValue < 200 or desiredTime < 0:
            desiredTime = 0
            displayNums(desiredTime, desiredTemp, currentTemp)
        switchValue = switch.read()
        enterValue = enter.read()
    if enterValue < 200:
        return [False, desiredTime]
    else:
        return [True, desiredTime]
    
def setTemp(desiredTime, desiredTemp, currentTemp):
    enterValue = enter.read()
    switchValue = switch.read()
    while (switchValue > 200 and enterValue > 200):
        up = upSwitch.read()
        down = downSwitch.read()
        clearValue = clear.read()
        if up < 200:
            desiredTemp += 1
            displayNums(desiredTime, desiredTemp, currentTemp)
            sleep(.4)
            up = upSwitch.read()
            while (up < 200):
                desiredTemp += 1
                displayNums(desiredTime, desiredTemp, currentTemp)
                sleep(.1)
                up = upSwitch.read()
        elif down < 200:
            desiredTemp -= 1
            displayNums(desiredTime, desiredTemp, currentTemp)
            sleep(.4)
            down = downSwitch.read()
            while (down < 200):
                desiredTemp -= 1
                displayNums(desiredTime, desiredTemp, currentTemp)
                sleep(.1)
                down = downSwitch.read()
        if clearValue < 200 or desiredTemp < 0:
            desiredTemp = 0
            displayNums(desiredTime, desiredTemp, currentTemp)
        switchValue = switch.read()
        enterValue = enter.read()
    if enterValue < 200:
        return [False, desiredTemp]
    else:
        return [True, desiredTemp]

#this starts the code!
if __name__ == '__main__':
    main()
