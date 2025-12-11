import ssl
from fastapi_mqtt import FastMQTT, MQTTConfig

from config import CA_CERT_PATH, HOST, PASSWORD, PORT, USERNAME

ctx = ssl.create_default_context(cafile=CA_CERT_PATH)
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_REQUIRED

mqttConfig = MQTTConfig(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    client_id="RPI_GATEWAY_01",
    ssl=ctx,
    keepalive=120,
)

mqtt = FastMQTT(config=mqttConfig)
