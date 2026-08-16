import json
import logging
import os

import paho.mqtt.client as mqtt

from storage import UserStorage

logger = logging.getLogger(__name__)

MQTT_HOST = os.environ.get("MQTT_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USER = os.environ.get("MQTT_USER", "")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")
MQTT_TOPIC_PREFIX = os.environ.get("MQTT_TOPIC_PREFIX", "keypad")
HA_EVENT_TOPIC = os.environ.get("HA_EVENT_TOPIC", "homeassistant/event/keypad_entry")
MAX_CODE_LENGTH = 20


class KeypadMQTT:
    def __init__(self, storage: UserStorage):
        self.storage = storage
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        if MQTT_USER:
            self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    def _on_connect(self, client, userdata, connect_flags, reason_code, properties):
        if reason_code == 0:
            topic = f"{MQTT_TOPIC_PREFIX}/+/code"
            client.subscribe(topic)
            logger.info("Connected to MQTT broker, subscribed to %s", topic)
        else:
            logger.error("MQTT connection failed: %s", reason_code)

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        logger.warning("Disconnected from MQTT broker (reason=%s)", reason_code)

    def _on_message(self, client, userdata, msg):
        if len(msg.payload) > MAX_CODE_LENGTH:
            logger.warning("Oversized payload (%d bytes) on %s, ignoring", len(msg.payload), msg.topic)
            return
        try:
            parts = msg.topic.split("/")
            device_id = parts[1] if len(parts) >= 3 else "unknown"
            code = msg.payload.decode("utf-8").strip()
            logger.debug("Code received from device %s", device_id)
            self._handle_code(device_id, code)
        except Exception:
            logger.exception("Error processing MQTT message on topic %s", msg.topic)

    def _handle_code(self, device_id: str, code: str):
        user = self.storage.find_user_by_code(code)
        if user:
            logger.info("Valid code entered by '%s' on device %s", user["name"], device_id)
            payload = json.dumps({
                "event_type": "keypad_code_entered",
                "device_id": device_id,
                "user_id": user["id"],
                "user_name": user["name"],
                "valid": True,
            })
            self.storage.add_history_entry({
                "device_id": device_id,
                "user_id": user["id"],
                "user_name": user["name"],
                "valid": True,
            })
        else:
            logger.warning("Invalid code entered on device %s", device_id)
            payload = json.dumps({
                "event_type": "keypad_invalid_code",
                "device_id": device_id,
                "valid": False,
            })
            self.storage.add_history_entry({
                "device_id": device_id,
                "user_id": None,
                "user_name": None,
                "valid": False,
            })

        self.client.publish(f"{MQTT_TOPIC_PREFIX}/event", payload, retain=False)
        self.client.publish(HA_EVENT_TOPIC, payload, retain=False)

    def start(self):
        try:
            self.client.connect_async(MQTT_HOST, MQTT_PORT)
            self.client.loop_start()
            logger.info("MQTT client connecting to %s:%s", MQTT_HOST, MQTT_PORT)
        except Exception:
            logger.exception("Failed to connect to MQTT broker at %s:%s", MQTT_HOST, MQTT_PORT)

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT client stopped")
