import time
import machine
import dht
import umqtt.robust


MQTT_CLIENT_ID = "ESP32_Hacienda"
CHANNEL_ID = "ID"
WRITE_API_KEY = "KEY"
MQTT_SERVER = "mqtt.thingspeak.com"
MQTT_TOPIC = "channels/" + CHANNEL_ID + "/publish/" + WRITE_API_KEY


class Cycle:
    def __init__(self, sensor, mqtt_client, topic):
        self.sensor = sensor
        self.mqtt_client = mqtt_client
        self.topic = topic

    def aquire(self):
        self.sensor.measure()
        temp = self.sensor.temperature()
        hum = self.sensor.humidity()
        return temp, hum

    def do(self):
        temp, hum = self.aquire()

        print("Temperature: %3.1f C" % temp)
        print("Humidity: %3.1f %%" % hum)

        payload = "field1=" + str(temp) + "&field2=" + str(hum)

        self.mqtt_client.publish(self.topic, payload)


def main():
    sensor = dht.DHT11(machine.Pin(4))
    mqtt_client = umqtt.robust.MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_SERVER)
    mqtt_client.connect()
    cycle = Cycle(sensor=sensor, mqtt_client=mqtt_client, topic=MQTT_TOPIC)

    while True:
        try:
            cycle.do()
        except Exception as e:
            print("Failed to perform the cycle: %s" % e)
        time.sleep(2)


main()
