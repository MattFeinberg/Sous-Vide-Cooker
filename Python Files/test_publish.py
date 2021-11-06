import paho.mqtt.client as mqtt #import the client1
import time

broker_address="192.168.86.29"

print("creating new instance")
client = mqtt.Client("P1") #create new instance

print("connecting to broker")
client.connect(broker_address) #connect to broker

print("Publishing message to topic","test_power")
client.publish("test_power","40")