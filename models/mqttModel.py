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


async def getPsk(endNode):
    # 1. SQL: 파이썬에서 받은 '문자열'을 UNHEX로 풀어서 비교
    # (주의: :id 앞뒤로 따옴표 붙이지 마세요. 그냥 :id 입니다)
    SQL = """
    SELECT psk, res_count
    FROM enddevice
    WHERE mac_address = UNHEX(:id)
    """

    try:
        # 2. Python 데이터 처리: 무조건 '순수 문자열(Hex String)'로 만듦
        if isinstance(endNode, bytes):
            # 바이트(b'\x07...')가 들어오면 -> "071d..." 문자열로 변환
            query_id = endNode.hex()
        elif isinstance(endNode, str):
            # 이미 문자열이면 그대로 사용, 단 '0x' 접두어가 있다면 제거 등의 처리 가능
            # 여기서는 순수 hex string("071d8512")이라고 가정
            query_id = endNode
        else:
            print(f"🚨 [getPsk] 타입 에러: {type(endNode)}는 처리할 수 없습니다.")
            return {"status": "FAIL"}

        # 3. 확인용 로그 (제대로 변환됐는지 확인)
        # 출력값이 b'...'가 아니라 "071d8512" 처럼 따옴표 안의 문자열이어야 함
        print(f"DEBUG: SQL 실행 -> UNHEX('{query_id}')")

        # 4. 쿼리 실행
        res = await db.fetch_one(query=SQL, values={"id": query_id})

        # 5. 결과 없음 처리
        if res is None:
            print(f"❌ [getPsk] DB 데이터 없음 (Target: {query_id})")
            return {"status": "FAIL"}

        return {"status": "OK", "data": dict(res)}

    except Exception as e:
        print(f"🚨 [getPsk] 최종 에러: {e}")
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
