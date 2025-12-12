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

        tmp = []
        for i in res["endNodes"]:
            tmp.append(base64.b64encode(i).decode("utf-8"))

        res["endNodes"] = tmp[:]
        print("LIST = ", res)
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
        endNode = base64.b64decode(data["target"]).hex()

        print("endNode", endNode)
        # 3. ★ 웹소켓으로 응답 전송 ★
        # "누가(serial)"에게 보낼지 인자로 꼭 넣어줘야 합니다!

        print(msg, endNode)
        res = await mqttModel.getPsk(endNode)

        data = res["data"]
        psk = data["psk"]
        res_count = data["res_count"]

        # 3. 7바이트: [6:13] (인덱스 6부터 13 미만까지)
        nonce = msg[8:15]

        # 4. 10바이트: [13:23] (인덱스 13부터 23 미만까지)
        ciphertext = msg[15:25]
        # 참고: 이 영역에 ASCII 문자 '16&8'이 포함되어 있습니다.

        # 5. 2바이트: [23:25] (인덱스 23부터 25 미만까지)
        tag = msg[25:]

        result = decrypt(psk, nonce, ciphertext, tag)

        counter = result["count"]
        parameter = result["parameter"]

        print(res_count, counter, parameter)

        if res_count > counter:
            print(f"[!] 폐기")
            return

        response_data = {"endNode": endNode, "parameter": parameter}

        await broadcast_mqtt_response(serial, response_data)
        print(f"[2] 웹소켓 전송 완료 -> {serial}")

        await mqttModel.updateReqCount(endNode, counter)

    except Exception as e:
        print(f"🚨 에러 발생: {e}")
        return
