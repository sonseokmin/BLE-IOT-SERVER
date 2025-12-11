import json
from models import httpModel
from schemas.schema import RequestModel
from services.sevice import encrypt
from mqtt.mqttClient import mqtt


# /remote 요청
async def remotePost(payload: RequestModel):
    endNode = payload.endNode
    cmdCategory = payload.cmdCategory
    cmdType = payload.cmdType
    parameter = payload.parameter

    print(
        "endNode =",
        endNode,
        "cmdCategory =",
        cmdCategory,
        "cmdType =",
        cmdType,
        "parameter =",
        parameter,
    )

    if not endNode or not cmdCategory or not cmdType or not parameter:
        return {"status": 400, "msg": "Bad Request"}

    try:
        res = await httpModel.getEndDevice(endNode)
        data = res["data"]

        # hex 코드 변환 로직
        req_count = data["req_count"].to_bytes(4, byteorder="big")
        cmdCategory = cmdCategory.to_bytes(1, byteorder="big")
        cmdType = cmdType.to_bytes(1, byteorder="big")
        parameter = parameter.to_bytes(4, byteorder="big")

        psk = data["psk"]
        serial = data["serial_number"]
        macAddress = data["mac_address"]

        plainText = req_count + cmdCategory + cmdType + parameter

        cipherValue = encrypt(plainText, psk)

        result = (
            b"\x11\xff"
            + macAddress
            + cipherValue["nonce"]
            + cipherValue["ciphertext"]
            + cipherValue["tag"]
        )

        print(result)

        if cmdCategory == 0:
            mqtt.client.publish(
                f"iot/{serial}/endNode/act",
                json.dumps({"target": endNode, "msg": result}),
                qos=0,
            )
        else:
            mqtt.client.publish(
                f"iot/{serial}/endNode/react",
                json.dumps({"target": endNode, "msg": result}),
                qos=0,
            )

    except Exception as e:
        print(e)


# /direct 요청
def directPost(payload: None):
    return {"status": 200, "mode": "direct"}
