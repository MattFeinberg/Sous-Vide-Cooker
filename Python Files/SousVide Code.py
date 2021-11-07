# Run this script on the ESP32 Sous Vide Machine
# All temperatures are in celsius
# This script will run the Sous Vide machine and send temperature and time data
# to the Raspberry Pi running the MQTT broker
# Note that variables mqtt_server, PLUG, ssid, password, and publish_directory
# should be changed to match an individual set up



import ssd1306, math
from machine import Pin, I2C, TouchPad
from time import sleep
from max6675 import MAX6675
import network
import urequests
from umqttsimple import MQTTClient

#Smart plug set up
mqtt_server = '192.168.86.38'  #IP Address
PLUG = 'ESPURNA-BF5B67'        #Smart plug ID

##Connect to Network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
networks = wlan.scan()

ssid = 'ssid'           #Input ssid here
password = 'password'   #Input password here
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
heatUp =  TouchPad(Pin(27))              ##ORANGE
switch = TouchPad(Pin(33))               ##BLUE
clear = TouchPad(Pin(12))                ##BROWN
cook = TouchPad(Pin(32))                 ##RED

#Some helpful variables
ON = 1
OFF = 0
power = OFF
accuracy = 1 #how accurate the temperature should be (plus/minus this number)
publish_directory = 'Second_steak_temp' #Change this for each cooking run to publish cooking data


def main():
    ### MAKRE SURE MACHINE IS OFF TO START ###
    sousVideOff()
    
    ### DISPLAY SET UP ###
    desiredTime = 0
    desiredTemp = 0
    currentTemp = therm.read()
    displayNums(desiredTime, desiredTemp, currentTemp, False)
    runTime = True
    settingNums = True
    
    ### GET TIME AND TEMP FROM USER ###
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
    
    ### HEAT UP TO DESIRED TEMP###
    heatUpWater(desiredTemp)
    
    ### BEGIN COOKING ###
    sousVideCook(desiredTemp, desiredTime)
    
    ### OFF ###
    if(power == ON):
        sousVideOff()
    client.publish('done_cooking', "yes")
    display.fill(0)
    display.text("Your food is", 5, 5)
    display.text("ready!", 5, 15)
    display.show()
    return
    

#This function takes care of turning the machine on and off to cook the food.
def sousVideCook(desiredTemp, desiredTime):
    currentTemp = therm.read()
    currentTime = desiredTime
    client.publish(publish_directory, str(currentTemp))
    displayNums(currentTime, desiredTemp, currentTemp, True)
    while currentTime > 0:
        sleep(60)
        currentTime = currentTime - 1
        currentTemp = therm.read()
        client.publish(publish_directory, str(currentTemp))
        displayNums(currentTime, desiredTemp, currentTemp, True)
        #Maintain Temp check
        if (currentTemp > (desiredTemp + accuracy)) and power == ON:
            sousVideOff()
        elif (currentTemp < (desiredTemp - accuracy)) and power == OFF:
            sousVideOn()

#Displays the numbers and text on the oled screen.
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

#Displays the waiting text and current temp vs desired
def displayWaiting(desiredTemp, currentTemp):
    display.fill(0)
    display.text("Heating up", 5, 5)
    display.text("Please wait...", 5, 15)
    display.text("Desired: " + str(desiredTemp), 5, 35)
    display.text("Current: " + str(currentTemp), 5, 45)
    display.show()

#This function takes input from the user to alter the desired time
def setTime(desiredTime, desiredTemp, currentTemp):
    heatUpValue = heatUp.read()
    switchValue = switch.read()
    while (switchValue > 200 and heatUpValue > 200):
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
        heatUpValue = heatUp.read()
    if heatUpValue < 200:
        return [False, desiredTime]
    else:
        return [True, desiredTime]

#This function takes input from the user to alter the desired temp
def setTemp(desiredTime, desiredTemp, currentTemp):
    heatUpValue = heatUp.read()
    switchValue = switch.read()
    while (switchValue > 200 and heatUpValue > 200):
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
        heatUpValue = heatUp.read()
    if heatUpValue < 200:
        return [False, desiredTemp]
    else:
        return [True, desiredTemp]

#This function heats up the machine to the desired temp to prepare for cooking
def heatUpWater(desiredTemp):
    #Get water to desired temp
    sousVideOn()
    print(str(power))
    currentTemp = therm.read()
    displayWaiting(desiredTemp, currentTemp)
    client.publish(publish_directory, str(currentTemp))
    while currentTemp < desiredTemp:
        sleep(60)
        currentTemp = therm.read()
        client.publish(publish_directory, str(currentTemp))
        displayWaiting(desiredTemp, currentTemp)
    #Keep water at desired temp until the user says its time to get cookin
    display.fill(0)
    display.text("Water is ready!",5, 5)
    display.text("Place your food in", 5, 15)
    display.text("and press cook", 5, 25)
    display.show()
    cookValue = cook.read()
    counter = 120  #use the counter so we dont send too many messages to the server
    while cookValue > 200:
        currentTemp = therm.read()
        if counter == 120:
            client.publish(publish_directory, str(currentTemp))
            counter = 0
            display.fill(0)
            display.text("Water is ready!",5, 5)
            display.text("Place your food in", 5, 15)
            display.text("and press cook", 5, 25)
            display.show()
        if ((currentTemp > (desiredTemp + accuracy)) and power == ON):
            sousVideOff()
        elif ((currentTemp < (desiredTemp - accuracy)) and power == OFF):
            sousVideOn()
        counter = counter + 1
        cookValue = cook.read()
        sleep(.5)

#These functions turn the machine on/off and update the state variable "power" accordingly
def sousVideOn():
    global power
    client.publish(PLUG + '/relay/0/set', '1')
    power = ON

def sousVideOff():
    global power
    client.publish(PLUG + '/relay/0/set', '0')
    power = OFF

#this starts the code!
if __name__ == '__main__':
    main()
