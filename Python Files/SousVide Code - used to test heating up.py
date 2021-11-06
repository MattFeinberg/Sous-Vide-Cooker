### COMMENTS ###


import ssd1306, math
from machine import Pin, I2C, TouchPad
from time import sleep
from max6675 import MAX6675
import network
import urequests
from umqttsimple import MQTTClient

#Smart plug set up
mqtt_server = '192.168.86.29'
PLUG = 'ESPURNA-BF5B67'

##Connect to Network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
networks = wlan.scan()

ssid = 'mattyfein'
password = 'lynnetapper'
print("Connecting to {}...".format(ssid))
wlan.connect(ssid, password)
while not wlan.isconnected():
    sleep(1)
    print('.')

print("Connected!")
print("IP address:", wlan.ifconfig()[0])

client = MQTTClient("clientID", mqtt_server)
client.connect()


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

#Some helpful variables
ON = 1
OFF = 0
power = OFF


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
    ### BEGIN COOKING ###
    sousVideCook(desiredTemp, desiredTime)
    
    ### OFF ###
    if(power == ON):
        sousVideOff()
    client.publish('done_cooking', "yes")
    display.poweroff()
    return
    

#This function takes care of turning the machine on and off to cook the food.
def sousVideCook(desiredTemp, desiredTime):
    sousVideOn()
    currentTemp = therm.read()
    currentTime = desiredTime
    client.publish('first_test_temp', str(currentTemp))
    displayNums(currentTime, desiredTemp, currentTemp, True)
    while currentTemp < desiredTemp:
        sleep(60)
        currentTime = currentTime - 1
        currentTemp = therm.read()
        client.publish('first_test_temp', str(currentTemp))
        displayNums(currentTime, desiredTemp, currentTemp, True)
    sousVideOff()

#Displays the numbers on the oled screen.
def displayNums(desiredTime, desiredTemp, currentTemp, cooking):
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
    #Display a star to indicate when the machine is on/cooking
    if cooking:
        display.text("*", 40, 15)
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
            displayNums(desiredTime, desiredTemp, currentTemp, False)
            sleep(.4)
            up = upSwitch.read()
            while (up < 200):
                desiredTime += 1
                displayNums(desiredTime, desiredTemp, currentTemp, False)
                sleep(.1)
                up = upSwitch.read()
        elif down < 200:
            desiredTime -= 1
            displayNums(desiredTime, desiredTemp, currentTemp, False)
            sleep(.4)
            down = downSwitch.read()
            while (down < 200):
                desiredTime -= 1
                displayNums(desiredTime, desiredTemp, currentTemp, False)
                sleep(.1)
                down = downSwitch.read()
        if clearValue < 200 or desiredTime < 0:
            desiredTime = 0
            displayNums(desiredTime, desiredTemp, currentTemp, False)
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
            displayNums(desiredTime, desiredTemp, currentTemp, False)
            sleep(.4)
            up = upSwitch.read()
            while (up < 200):
                desiredTemp += 1
                displayNums(desiredTime, desiredTemp, currentTemp, False)
                sleep(.1)
                up = upSwitch.read()
        elif down < 200:
            desiredTemp -= 1
            displayNums(desiredTime, desiredTemp, currentTemp, False)
            sleep(.4)
            down = downSwitch.read()
            while (down < 200):
                desiredTemp -= 1
                displayNums(desiredTime, desiredTemp, currentTemp, False)
                sleep(.1)
                down = downSwitch.read()
        if clearValue < 200 or desiredTemp < 0:
            desiredTemp = 0
            displayNums(desiredTime, desiredTemp, currentTemp, False)
        switchValue = switch.read()
        enterValue = enter.read()
    if enterValue < 200:
        return [False, desiredTemp]
    else:
        return [True, desiredTemp]
# Look at my_freezer_testfile - must set up client then use client.publish    
def sousVideOn():
    client.publish(PLUG + '/relay/0/set', '1')
    power = ON

def sousVideOff():
    client.publish(PLUG + '/relay/0/set', '0')
    power = OFF

#this starts the code!
if __name__ == '__main__':
    main()
