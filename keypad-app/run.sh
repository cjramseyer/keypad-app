#!/usr/bin/with-contenv bashio

# Read add-on configuration
export LOG_LEVEL
export MQTT_TOPIC_PREFIX
export MQTT_HOST
export MQTT_PORT
export MQTT_USER
export MQTT_PASSWORD
export HA_EVENT_TOPIC
export API_KEY
export INGRESS_PATH

LOG_LEVEL=$(bashio::config 'log_level')
MQTT_TOPIC_PREFIX=$(bashio::config 'mqtt_topic_prefix')
HA_EVENT_TOPIC=$(bashio::config 'ha_event_topic')
API_KEY=$(bashio::config 'api_key')
INGRESS_PATH=$(bashio::addon 'ingress_entry')

# Prefer the HA-managed MQTT broker; fall back to manual config
if bashio::services.available "mqtt"; then
    MQTT_HOST=$(bashio::services "mqtt" "host")
    MQTT_PORT=$(bashio::services "mqtt" "port")
    MQTT_USER=$(bashio::services "mqtt" "username")
    MQTT_PASSWORD=$(bashio::services "mqtt" "password")
    bashio::log.info "Using Home Assistant MQTT broker at ${MQTT_HOST}:${MQTT_PORT}"
else
    MQTT_HOST=$(bashio::config 'mqtt_host')
    MQTT_PORT=$(bashio::config 'mqtt_port')
    MQTT_USER=$(bashio::config 'mqtt_user')
    MQTT_PASSWORD=$(bashio::config 'mqtt_password')
    bashio::log.info "Using configured MQTT broker at ${MQTT_HOST}:${MQTT_PORT}"
fi

bashio::log.info "Starting Keypad Manager..."
cd /app || exit 1
exec python3 app.py