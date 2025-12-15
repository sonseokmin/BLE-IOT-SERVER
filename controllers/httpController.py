import base64
import json
from models import httpModel
from schemas.schema import RequestModel, RequestDecryptModel
from services.sevice import encrypt, decrypt
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
        print(res)

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

        print("mac_address = ", macAddress, len(macAddress))
        print("nonce = ", cipherValue["nonce"], len(cipherValue["nonce"]))
        print(
            "ciphertext = ", cipherValue["ciphertext"], len(cipherValue["ciphertext"])
        )
        print("tag = ", cipherValue["tag"], len(cipherValue["tag"]))
        print("result = ", result, len(result))

        if tmp == 0:
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

        psk = data["psk"]
        macAddress = data["mac_address"]

        # hex 코드 변환 로직
        req_count = data["req_count"]
        psk = data["psk"]
        macAddress = data["mac_address"]

        cipherValue = encrypt(psk, req_count, cmdCategory, cmdType, parameter)

        result = (
            b"\x1e\xff\x11\xff"
            + macAddress
            + cipherValue["nonce"]
            + cipherValue["ciphertext"]
            + cipherValue["tag"]
        )

        print("result =", base64.b64encode(result).decode("utf-8"))
        await httpModel.updateReqCount(endNode)

        return {
            "status": 200,
            "target": base64.b64encode(macAddress).decode("utf-8"),
            "msg": base64.b64encode(result).decode("utf-8"),
        }

    except Exception as e:
        print(e)


async def decryptPost(payload: RequestDecryptModel):
    target = payload.target
    msg = payload.msg

    print("target =", target, "msg =", msg)

    if target is None or msg is None:
        return {"status": 400, "msg": "Bad Request"}

    msg = base64.b64decode(msg)
    target = base64.b64decode(target).hex()

    print("target =", target, "msg =", msg)

    try:
        res = await httpModel.getPsk(target)
        data = res["data"]

        psk = data["psk"]

        # 3. 7바이트: [6:13] (인덱스 6부터 13 미만까지)
        nonce = msg[8:15]

        # 4. 10바이트: [13:23] (인덱스 13부터 23 미만까지)
        ciphertext = msg[15:25]
        # 참고: 이 영역에 ASCII 문자 '16&8'이 포함되어 있습니다.

        # 5. 2바이트: [23:25] (인덱스 23부터 25 미만까지)
        tag = msg[25:]

        print(f"msg: {msg}\n nonce: {nonce} ciphertext:{ciphertext} tag:{tag}")

        result = decrypt(psk, nonce, ciphertext, tag)

        cmdCategory = result["cmdCategory"]
        cmdType = result["cmdType"]
        parameter = result["parameter"]

        if cmdType == 0:
            return

        return {"status": 200, f"{cmdCategory}": parameter}

    except Exception as e:
        print(e)
