import time
import machine
import dht
import umqtt.robust


MQTT_CLIENT_ID = "ESP32_Hacienda"
MQTT_SERVER = "MYHOMESERVER"
MQTT_PORT = 26883
MQTT_TOPIC_TEMP = "pete/test/temperature"
MQTT_TOPIC_HUM = "pete/test/humidity"
MQTT_TOPIC_CTRL = "pete/test/control"


class Cycle:
    def __init__(self, sensor, mqtt_client, topic_temp, topic_hum):
        self.sensor = sensor
        self.mqtt_client = mqtt_client
        self.topic_temp = topic_temp
        self.topic_hum = topic_hum

    def aquire(self):
        self.sensor.measure()
        temp = self.sensor.temperature()
        hum = self.sensor.humidity()
        return temp, hum

    def do(self):
        temp, hum = self.aquire()

        print("Temperature: %3.1f C" % temp)
        print("Humidity: %3.1f %%" % hum)

        self.mqtt_client.publish(self.topic_temp, str(temp))
        self.mqtt_client.publish(self.topic_hum, str(hum))


class Dioder:
    def __init__(self, led):
        self.led = led

    def message_callback(self, unused_topic, msg):
        if msg == b"on":
            print("Got on")
            self.led.value(0)
        elif msg == b"off":
            print("Got off")
            self.led.value(1)


def main():
    sensor = dht.DHT11(machine.Pin(4))
    led = machine.Pin(25, machine.Pin.OUT, value=1)
    mqtt_client = umqtt.robust.MQTTClient(
        client_id=MQTT_CLIENT_ID, server=MQTT_SERVER, port=MQTT_PORT
    )
    dioder = Dioder(led)

    mqtt_client.connect()
    mqtt_client.set_callback(dioder.message_callback)
    mqtt_client.subscribe(MQTT_TOPIC_CTRL)

    cycle = Cycle(
        sensor=sensor,
        mqtt_client=mqtt_client,
        topic_temp=MQTT_TOPIC_TEMP,
        topic_hum=MQTT_TOPIC_HUM,
    )

    while True:
        try:
            mqtt_client.check_msg()
        except Exception as e:
            print("Failed process the message: %s" % e)

        try:
            cycle.do()
        except Exception as e:
            print("Failed to perform the cycle: %s" % e)
        time.sleep(2)


main()
