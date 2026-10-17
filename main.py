from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import ssl
import os

app = Flask(__name__)

MQTT_HOST = "b0517d51.ala.eu-central-1.emqxsl.com"
MQTT_PORT = 8883
MQTT_USER = "lisiy19781@rambler.ru"
MQTT_PASS = "Novik_04041978_Elena_!"

def send_mqtt_cmd(topic, value):
    try:
        client = mqtt.Client()
        client.username_pw_set(MQTT_USER, MQTT_PASS)
        client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)
        client.connect(MQTT_HOST, MQTT_PORT, 10)
        client.publish(topic, value)
        client.disconnect()
        print(f"[MQTT] {topic} -> {value}")
    except Exception as e:
        print(f"[MQTT ERROR] {e}")

@app.route('/v1.0', methods=['HEAD', 'GET'])
@app.route('/v1.0/user/unlink', methods=['POST'])
def check_status():
    req_id = request.headers.get('X-Request-Id', 'req-123')
    return ('', 200, {'X-Request-Id': req_id})

@app.route('/v1.0/user/devices', methods=['GET'])
def get_devices():
    req_id = request.headers.get('X-Request-Id', 'req-123')
    return jsonify({
        "request_id": req_id,
        "payload": {
            "user_id": "ghost_hacker_1",
            "devices": [
                {
                    "id": "relay1",
                    "name": "Главный свет",
                    "description": "Люстра на ESP32-S3",
                    "room": "Гостиная",
                    "type": "devices.types.light",
                    "capabilities": [
                        {
                            "type": "devices.capabilities.on_off",
                            "retrievable": True,
                            "parameters": {"split": False}
                        }
                    ]
                }
            ]
        }
    }), 200, {'X-Request-Id': req_id}

@app.route('/v1.0/user/devices/action', methods=['POST'])
def action_devices():
    req_id = request.headers.get('X-Request-Id', 'req-123')
    body = request.get_json(force=True)
    devices_res = []

    for dev in body.get('payload', {}).get('devices', []):
        dev_id = dev.get('id')
        caps_res = []
        for cap in dev.get('capabilities', []):
            if cap.get('type') == 'devices.capabilities.on_off':
                val = cap.get('state', {}).get('value', False)
                state_str = "ON" if val else "OFF"
                send_mqtt_cmd(f"alice/cmd/{dev_id}", state_str)
                caps_res.append({
                    "type": "devices.capabilities.on_off",
                    "state": {"percent": None, "status": "DONE", "value": val}
                })
        devices_res.append({"id": dev_id, "capabilities": caps_res})

    return jsonify({"request_id": req_id, "payload": {"devices": devices_res}}), 200, {'X-Request-Id': req_id}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
