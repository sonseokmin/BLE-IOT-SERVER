# models/sensor_dao.py
from database.database import db


async def register(serial: str):

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
