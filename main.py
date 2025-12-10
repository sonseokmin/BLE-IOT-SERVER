from fastapi import FastAPI
from mqtt.mqttClient import mqtt
from routes import httpRoute, mqttRoute

app = FastAPI()

mqtt.init_app(app)

app.include_router(httpRoute.router)




