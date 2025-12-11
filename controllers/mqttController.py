from models import mqttModel
import json


async def registerMqtt(client, topic, payload, qos, properties):
    print(f"[1] {topic} 요청")
    try:
        data = json.loads(payload.decode())
        serial = data["serial"]

        res = await mqttModel.register(serial)

        if res["status"] == "FAIL":
            return

        print(f"[2] {serial} register ACK 전송")
        client.publish(f"iot/{serial}/register/ack", json.dumps({"rpi_serial": serial}))

    except Exception as e:
        print(e)
        return


async def endnodeMqtt(client, topic, payload, qos, properties):
    node = topic.split("/")[1]
    print(f"[MQTT] endNode ({node}) →", payload.decode())


async def endnodeRegisterMqtt(client, topic, payload, qos, properties):
    node = topic.split("/")[1]
    print(f"[MQTT] endNode/register ({node}) →", payload.decode())


async def ackMqtt(client, topic, payload, qos, properties):
    node = topic.split("/")[1]
    print(f"[MQTT] act/ack ({node}) →", payload.decode())
