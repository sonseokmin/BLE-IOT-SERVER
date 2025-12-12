import base64
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
    tmp = cmdCategory
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

    if endNode is None or cmdCategory is None or cmdType is None or parameter is None:
        return {"status": 400, "msg": "Bad Request"}

    try:
        res = await httpModel.getEndDevice(endNode)
        data = res["data"]

        # hex 코드 변환 로직
        req_count = data["req_count"]
        psk = data["psk"]
        serial = data["serial_number"]
        macAddress = data["mac_address"]

        cipherValue = encrypt(psk, req_count, cmdCategory, cmdType, parameter)

        result = (
            b"\x1e\xff\x11\xff"
            + macAddress
            + cipherValue["nonce"]
            + cipherValue["ciphertext"]
            + cipherValue["tag"]
        )

        print("result", result)
        if tmp == 1:
            mqtt.client.publish(
                f"iot/{serial}/endNode/act",
                json.dumps(
                    {
                        "target": base64.b64encode(macAddress).decode("utf-8"),
                        "msg": base64.b64encode(result).decode("utf-8"),
                    }
                ),
                qos=0,
            )
        else:
            mqtt.client.publish(
                f"iot/{serial}/endNode/react",
                json.dumps(
                    {
                        "target": base64.b64encode(macAddress).decode("utf-8"),
                        "msg": base64.b64encode(result).decode("utf-8"),
                    }
                ),
                qos=0,
            )

        await httpModel.updateReqCount(endNode)

    except Exception as e:
        print(e)


# /direct 요청
async def directPost(payload: RequestModel):
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

    if endNode is None or cmdCategory is None or cmdType is None or parameter is None:
        return {"status": 400, "msg": "Bad Request"}

    try:
        res = await httpModel.getEndDevice(endNode)
        data = res["data"]

        # hex 코드 변환 로직
        req_count = data["req_count"].to_bytes(4, byteorder="little")
        cmdCategory = cmdCategory.to_bytes(1, byteorder="little")
        cmdType = cmdType.to_bytes(1, byteorder="little")
        parameter = parameter.to_bytes(4, byteorder="little")

        psk = data["psk"]
        macAddress = data["mac_address"]

        plainText = req_count + cmdCategory + cmdType + parameter

        print(plainText)

        cipherValue = encrypt(plainText, psk)

        result = (
            b"\x1e\xff\x11\xff"
            + macAddress
            + cipherValue["nonce"]
            + cipherValue["ciphertext"]
            + cipherValue["tag"]
        )

        await httpModel.updateReqCount(endNode)

        return {
            "status": 200,
            "target": endNode,
            "msg": base64.b64encode(result).decode("utf-8"),
        }

    except Exception as e:
        print(e)
