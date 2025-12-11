from mqtt.mqttRouter import MQTTRouter
from controllers.mqttController import (
    gatewayRegisterMqtt,
    endnodeListMqtt,
    endnodeRegisterMqtt,
    ackMqtt,
    reactMqtt,
)

router = MQTTRouter()

# 1) iot/register
router.add("iot/register", gatewayRegisterMqtt)

# 2) iot/+/endNode
router.add("iot/+/endNode", endnodeListMqtt)

# 3) iot/+/endNode/register
router.add("iot/+/endNode/register", endnodeRegisterMqtt)

# 4) iot/+/endNode/act/ack
router.add("iot/+/endNode/act/ack", ackMqtt)

# 5) iot/+/endNode/react/ack
router.add("iot/+/endNode/react/ack", reactMqtt)
