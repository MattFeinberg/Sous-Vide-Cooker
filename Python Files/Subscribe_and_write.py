# This script runs on a Raspberry Pi that is running a an MQTT broker to let the ESP32 Sous Vide
# machine document temperature and time data from a cooking run.
# Note: Must change topic name at various marked locations in the file before running

import paho.mqtt.client as mqtt
import time

#################
def on_message(client, userdata, message):
    # This is what will happen any time a message is reviecved.
    
    if message.topic == "first_steak_temp":    ##CHANGE TOPIC NAME!
        temp_file.write("{},{}\n".format(time.time(), str(message.payload.decode("utf-8"))))
    elif message.topic == (PLUG + '/power'):
        power_file.write("{},{}\n".format(time.time(), str(message.payload.decode("utf-8"))))
    elif message.topic == "done_cooking":
        print("closing file")
        temp_file.close()
        power_file.close()
        client.loop_stop()
#################
host = "192.168.86.38"
PLUG = "ESPURNA-BF5B67"
client_name = "testing"

temp_file = open('second_steak_temp.csv', 'w')   #Change FILE NAME!!
temp_file.write("timestamp,value\n")
power_file = open('second_steak_power.csv', 'w') #Change FILE NAME!!
power_file.write("timestamp,value\n")

print("creating new instance")
client = mqtt.Client(client_name)
client.on_message = on_message

print("connecting to broker")
client.connect(host)
client.loop_start()

print("subscribing to all topics! '#' ")
client.subscribe("#")

while True: 
    time.sleep(60)

