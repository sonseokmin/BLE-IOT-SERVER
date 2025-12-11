import base64
from models import mqttModel
import json
from services.sevice import decrypt
from routes.websocketRoute import broadcast_mqtt_response


async def gatewayRegisterMqtt(client, topic, payload, qos, properties):
    print(f"[1] {topic} 요청")
    try:
        data = json.loads(payload.decode())
        serial = data["serial"]

        res = await mqttModel.gatewayRegister(serial)

        if res["status"] == "FAIL":
            return

        print(f"[2] {serial} register ACK 전송")
        client.publish(
            f"iot/{serial}/register/ack", json.dumps({"rpi_serial": serial}), qos=0
        )

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
        client.publish(
            f"iot/{serial}/endNode/ack",
            json.dumps(res),
            qos=0,
        )

    except Exception as e:
        print(e)
        return


async def endnodeRegisterMqtt(client, topic, payload, qos, properties):
    print(f"[1] {topic} 요청")
    try:
        serial = topic.split("/")[1]

        data = json.loads(payload.decode())
        endNode = base64.b64decode(data["endNode"])

        res = await mqttModel.endNodeRegister(serial, endNode)

        if res["status"] == "FAIL":
            return

        print(f"[2] {serial} {endNode} endNodeRegister ACK 전송")
        client.publish(
            f"iot/{serial}/endNode/register/ack", json.dumps({"res": "ok"}), qos=0
        )

    except Exception as e:
        print(e)
        return


async def ackMqtt(client, topic, payload, qos, properties):
    print(f"[1] {topic} 요청 수신")

    try:
        # 1. 토픽에서 시리얼 번호 추출 (iot/1234/act/ack -> 1234)
        serial = topic.split("/")[1]

        # 2. Payload 디코딩 (Bytes -> JSON)
        decoded_payload = json.loads(payload.decode())

        # 3. ★ 웹소켓으로 응답 전송 ★
        # "누가(serial)"에게 보낼지 인자로 꼭 넣어줘야 합니다!
        response_data = {
            "type": "ACK",
            "res": decoded_payload.get("res", "No Content"),
            "serial": serial,
        }

        await broadcast_mqtt_response(serial, response_data)
        print(f"[2] 웹소켓 전송 완료 -> {serial}")

    except Exception as e:
        print(f"🚨 에러 발생: {e}")
        return


async def reactMqtt(client, topic, payload, qos, properties):
    print(f"[1] {topic} 요청 수신")

    try:
        # 1. 토픽에서 시리얼 번호 추출 (iot/1234/act/ack -> 1234)
        serial = topic.split("/")[1]
        # 2. Payload 디코딩 (Bytes -> JSON)
        data = json.loads(payload.decode())

        msg = base64.b64decode(data["msg"])
        endNode = data["target"]
        # 3. ★ 웹소켓으로 응답 전송 ★
        # "누가(serial)"에게 보낼지 인자로 꼭 넣어줘야 합니다!

        print(msg, endNode)
        res = await mqttModel.getPsk(endNode)
        psk = res["data"]["psk"]

        result = decrypt(msg, psk)["plaintext"]

        parameter = int.from_bytes(result[6:10], "big")
        print(parameter)

        response_data = {"endNode": endNode, "parameter": parameter}

        await broadcast_mqtt_response(serial, response_data)
        print(f"[2] 웹소켓 전송 완료 -> {serial}")

    except Exception as e:
        print(f"🚨 에러 발생: {e}")
        return
