# models/sensor_dao.py
from database.database import db


async def gatewayRegister(serial: str):

    SQL = """
    INSERT INTO gateway (serial_number, status, last_seen)
    VALUES (:serial, :status, NOW())
    """

    try:
        await db.execute(query=SQL, values={"serial": serial, "status": 1})

        # 등록 성공시
        print(f"[DB 저장] {serial}")
        return {"status": "OK"}

    except Exception as e:
        # 이미 등록된 GateWay일 경우 재전송
        if hasattr(e, "args") and len(e.args) > 0 and e.args[0] == 1062:
            print(f"[DB 중복] {serial}")
            return {"status": "CONFLICT"}

        # 등록 실패
        print(f"[DB 에러] 저장 실패: {e}")
        return {"status": "FAIL"}


async def endNodeList(serial: str):
    SQL = """
    SELECT
    enddevice.mac_address
    FROM
        gre
    JOIN
        gateway ON (gre.gateway_id = gateway.id)
    JOIN
        enddevice ON (gre.enddevice_id = enddevice.id) -- enddevice 테이블 조인
    WHERE
        gateway.serial_number = :serial;
    """

    try:
        res = await db.fetch_all(query=SQL, values={"serial": serial})
        # 등록 성공시
        print(f"[DB 조회] {serial}")
        endnode_ids = [list(row.values())[0] for row in res]
        return {"status": "OK", "endNodes": endnode_ids}

    except Exception as e:
        # 등록 실패
        print(f"[DB 에러] 조회 실패: {e}")
        return {"status": "FAIL"}


async def endNodeRegister(serial: str, endNode: str):
    SQL = """
    INSERT INTO gre (gateway_id, enddevice_id)
    SELECT 
    (SELECT id FROM gateway WHERE serial_number = :serial) AS gateway_id,
    (SELECT id FROM enddevice WHERE mac_address = :endNode) AS enddevice_id;
    """

    try:
        await db.execute(query=SQL, values={"serial": serial, "endNode": endNode})

        # 등록 성공시
        print(f"[DB 저장] {serial} {endNode}")
        return {"status": "OK"}

    except Exception as e:
        # 이미 등록된 값일 경우 재전송
        if hasattr(e, "args") and len(e.args) > 0 and e.args[0] == 1062:
            print(f"[DB 중복] {serial} {endNode}")
            return {"status": "CONFLICT"}

        # 등록 실패
        print(f"[DB 에러] 저장 실패: {e}")
        return {"status": "FAIL"}


async def getPsk(endNode: str):
    SQL = """
    SELECT psk, res_count
    FROM enddevice
    WHERE mac_address = UNHEX(:id)
    """

    if isinstance(endNode, bytes):
        query_id = endNode.hex()
    else:
        # 이미 문자열(Hex String)이라면 그대로 사용
        query_id = endNode

    try:
        res = await db.fetch_one(query=SQL, values={"id": query_id})
        return {"status": "OK", "data": dict(res)}

    except Exception as e:
        print(e)
        return {"status": "FAIL"}


async def updateReqCount(endNode: str, counter: int):
    SQL = """
    UPDATE enddevice
    SET res_count = :counter + 1
    WHERE id = :id
    """

    try:
        res = await db.execute(query=SQL, values={"counter": counter, "id": endNode})

        return {"status": "OK"}

    except Exception as e:
        print(e)
        return {"status": "FAIL"}
