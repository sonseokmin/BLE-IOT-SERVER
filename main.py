from fastapi import FastAPI
from mqtt.mqttClient import mqtt
from routes import httpRoute, mqttRoute, websocketRoute
from contextlib import asynccontextmanager
from database.database import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # [1. 서버 켜질 때] -----------------------
    print("🚀 서버 시작: 리소스 연결 중...")

    # 1) DB 연결
    await db.connect()
    print("✅ DB 연결 성공!")

    # 2) MQTT 연결 (★ 이 코드를 여기에 직접 넣어야 합니다!)
    await mqtt.mqtt_startup()
    print("✅ MQTT 브로커 연결 성공!")

    yield  # -------------------------------- [앱 작동 중]

    # [2. 서버 꺼질 때] -------------------------
    print("💤 서버 종료: 리소스 해제 중...")

    # 3) MQTT 해제
    await mqtt.mqtt_shutdown()
    print("👋 MQTT 연결 해제 완료")

    # 4) DB 해제
    await db.disconnect()
    print("👋 DB 연결 해제 완료")


app = FastAPI(lifespan=lifespan)

mqtt.init_app(app)

app.include_router(httpRoute.router)
app.include_router(websocketRoute.router)
