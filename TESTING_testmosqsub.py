#! /usr/bin/python

import paho.mqtt.client as mqtt
import time

broker_addr = "127.0.0.1"
sub = "home/office/#"
#thinking about /home/DHT11/<room>/<sensor> 

def on_connect(client, userdata, flags, rc):
	m="Connected flags" + str(flags) + " result code " + str(rc) + " client id: " + str(client)
	print(m)
	client.subscribe(sub)
		
def on_message(client1, userdata, message):
	print("message received from '" + str(message.topic) + "': " + str(message.payload.decode("utf-8")))

def on_subscribe(client, obj, mid, qos):
	print("Subscribed: " + str(mid) + " " + str(qos))
	
client1 = mqtt.Client()
client1.on_connect= on_connect
client1.on_message= on_message
client1.on_subscribe= on_subscribe

client1.connect(broker_addr, 1883, 60)
client1.loop_start()

while 1:
	time.sleep(1)
	
client1.loop_stop()
client1.disconnect()
