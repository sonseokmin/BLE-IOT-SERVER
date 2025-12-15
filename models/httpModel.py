from database.database import db


async def getEndDevice(endNode: str):
    SQL = """
    SELECT e.mac_address, e.psk, e.req_count, gw.serial_number
    FROM enddevice e
    INNER JOIN gre g ON e.id = g.enddevice_id
    INNER JOIN gateway gw ON g.gateway_id = gw.id
    WHERE e.id = :id;
    """

    try:
        res = await db.fetch_one(query=SQL, values={"id": endNode})

        return {"status": "OK", "data": dict(res)}

    except Exception as e:
        print(e)
        return {"status": "FAIL"}


async def updateReqCount(
    endNode: str,
):
    SQL = """
    UPDATE enddevice
    SET req_count = req_count + 1
    WHERE id = :id
    """

    try:
        res = await db.execute(query=SQL, values={"id": endNode})

        return {"status": "OK"}

    except Exception as e:
        print(e)
        return {"status": "FAIL"}


async def getPsk(target):
    # 1. SQL: 파이썬에서 받은 '문자열'을 UNHEX로 풀어서 비교
    # (주의: :id 앞뒤로 따옴표 붙이지 마세요. 그냥 :id 입니다)
    SQL = """
    SELECT psk
    FROM enddevice
    WHERE mac_address = :id;
    """

    try:
        # 3. 확인용 로그 (제대로 변환됐는지 확인)
        # 출력값이 b'...'가 아니라 "071d8512" 처럼 따옴표 안의 문자열이어야 함
        print(f"DEBUG: SQL 실행 -> {target}')")

        # 4. 쿼리 실행
        print(type(target))
        res = await db.fetch_one(query=SQL, values={"id": bytes.fromhex(target)})
        # res = await db.fetch_one(query=SQL)

        # 5. 결과 없음 처리
        if res is None:
            print(f"❌ [getPsk] DB 데이터 없음 (Target: {target})")
            return {"status": "FAIL"}
        print(dict(res))

        return {"status": "OK", "data": dict(res)}

    except Exception as e:
        print(f"🚨 [getPsk] 최종 에러: {e}")
        return {"status": "FAIL"}
