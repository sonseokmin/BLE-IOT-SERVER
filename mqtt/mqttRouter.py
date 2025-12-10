# mqtt/mqttRouter.py

from mqtt.mqttClient import mqtt

class MQTTRouter:
    def __init__(self, prefix: str = ""):
        self.prefix = prefix.strip("/")

    def route(self, topic: str):
        full_topic = f"{self.prefix}/{topic}".strip("/") if self.prefix else topic

        def decorator(func):
            mqtt.subscribe(full_topic)(func)
            return func

        return decorator

    def add(self, topic: str, handler):
        """ Function-style registration """
        full_topic = f"{self.prefix}/{topic}".strip("/") if self.prefix else topic
        mqtt.subscribe(full_topic)(handler)
