import ssl
from fastapi_mqtt import FastMQTT, MQTTConfig

from config import CA_CERT_PATH

ctx = ssl.create_default_context(cafile=CA_CERT_PATH)
ctx.check_hostname = False        
ctx.verify_mode = ssl.CERT_REQUIRED

mqttConfig = MQTTConfig(
    host="127.0.0.1",
    port=8883,
    username="sechang",
    password="1234",
    client_id="RPI_GATEWAY_01",
    ssl=ctx,
    keepalive=120
)

mqtt = FastMQTT(config=mqttConfig)
