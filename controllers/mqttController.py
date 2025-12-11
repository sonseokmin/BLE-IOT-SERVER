from models import mqttModel
import json


async def gatewayRegisterMqtt(client, topic, payload, qos, properties):
    print(f"[1] {topic} 요청")
    try:
        data = json.loads(payload.decode())
        serial = data["serial"]

        res = await mqttModel.gatewayRegister(serial)

        if res["status"] == "FAIL":
            return

        print(f"[2] {serial} register ACK 전송")
        client.publish(f"iot/{serial}/register/ack", json.dumps({"rpi_serial": serial}))

    except Exception as e:
        print(e)
        return


async def endnodeListMqtt(client, topic, payload, qos, properties):
    print(f"[1] {topic} 요청")
    try:
        serial = topic.split("/")[1]
        res = await mqttModel.endNodeList(serial)

        if res["status"] == "FAIL":
            return

        print(f"[2] {serial} endNode ACK 전송")
        client.publish(f"iot/{serial}/endNode/ack", json.dumps({"endNodes": res}))

    except Exception as e:
        print(e)
        return


async def endnodeRegisterMqtt(client, topic, payload, qos, properties):
    print(f"[1] {topic} 요청")
    try:
        serial = topic.split("/")[1]

        data = json.loads(payload.decode())
        endNode = data["endNode"]

        res = await mqttModel.endNodeRegister(serial, endNode)

        if res["status"] == "FAIL":
            return

        print(f"[2] {serial} {endNode} endNodeRegister ACK 전송")
        client.publish(f"iot/{serial}/endNode/register/ack", json.dumps({"res": "ok"}))

    except Exception as e:
        print(e)
        return


async def ackMqtt(client, topic, payload, qos, properties):
    node = topic.split("/")[1]
    print(f"[MQTT] act/ack ({node}) →", payload.decode())
