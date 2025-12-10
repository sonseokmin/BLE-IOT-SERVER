async def registerMqtt(client, topic, payload, qos, properties):
    print("[MQTT] register →", payload.decode())

async def endnodeMqtt(client, topic, payload, qos, properties):
    node = topic.split("/")[1]
    print(f"[MQTT] endNode ({node}) →", payload.decode())

async def endnodeRegisterMqtt(client, topic, payload, qos, properties):
    node = topic.split("/")[1]
    print(f"[MQTT] endNode/register ({node}) →", payload.decode())

async def ackMqtt(client, topic, payload, qos, properties):
    node = topic.split("/")[1]
    print(f"[MQTT] act/ack ({node}) →", payload.decode())
