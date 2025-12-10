
from mqtt.mqttRouter import MQTTRouter
from controllers.mqttController import (
    registerMqtt,
    endnodeMqtt,
    endnodeRegisterMqtt,
    ackMqtt,
)

router = MQTTRouter()

# 1) iot/register
router.add("iot/register", registerMqtt)

# 2) iot/+/endNode
router.add("iot/+/endNode", endnodeMqtt)

# 3) iot/+/endNode/register
router.add("iot/+/endNode/register", endnodeRegisterMqtt)

# 4) iot/+/endNode/act/ack
router.add("iot/+/endNode/act/ack", ackMqtt)
