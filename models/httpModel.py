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
