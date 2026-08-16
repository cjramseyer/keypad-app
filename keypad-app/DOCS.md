# Home Assistant Add-on: Keypad Manager

Keypad Manager is a Python-based Home Assistant add-on that stores and
validates user PIN codes, listens for keypad input over MQTT, and fires
Home Assistant events when a code is entered — valid or invalid.

## How it works

1. A keypad device publishes a PIN to the MQTT topic
   `<prefix>/<device_id>/code` (e.g. `keypad/front-door/code`).
2. The add-on validates the PIN against the stored user list.
3. It publishes the result to two MQTT topics:
   - `<prefix>/event` — general keypad event
   - `homeassistant/event/keypad_entry` — consumed by HA automations
4. The entry is recorded in the history log visible in the web dashboard.

## Installation

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**.
2. Click the menu (⋮) and choose **Repositories**.
3. Add `https://github.com/cjramseyer/keypad-app` and click **Add**.
4. Find **Keypad Manager** in the store and click **Install**.
5. Configure the add-on (see below), then click **Start**.
6. Open the web UI via **Open Web UI** or the sidebar panel.

## Configuration

**Note**: _Restart the add-on after changing any configuration option._

Example configuration:

```yaml
log_level: info
mqtt_topic_prefix: keypad
mqtt_host: ""
mqtt_port: 1883
mqtt_user: ""
mqtt_password: ""
```

### Option: `log_level`

Controls the verbosity of add-on log output. Possible values:

- `trace`: Every internal function call.
- `debug`: Detailed debug information.
- `info`: Normal events (recommended default).
- `notice`: Significant but non-error events.
- `warning`: Unexpected but recoverable situations.
- `error`: Runtime errors that need attention.
- `fatal`: Add-on is no longer functional.

### Option: `mqtt_topic_prefix`

The MQTT topic prefix used for all keypad messages. Defaults to `keypad`.

Keypad devices must publish PIN codes to `<prefix>/<device_id>/code`.
The add-on publishes events to `<prefix>/event`.

### Option: `mqtt_host`

Hostname or IP address of your MQTT broker.

**Leave blank** when using the Home Assistant Mosquitto add-on — the
add-on will automatically connect to it using the `mqtt` service.

### Option: `mqtt_port`

Port of your MQTT broker. Defaults to `1883`.

### Option: `mqtt_user`

MQTT broker username. Leave blank when using the Mosquitto add-on.

### Option: `mqtt_password`

MQTT broker password. Leave blank when using the Mosquitto add-on.

## MQTT topics

| Topic | Direction | Description |
|---|---|---|
| `<prefix>/<device_id>/code` | Subscribe | Keypad device publishes a PIN here |
| `<prefix>/event` | Publish | Result of every code attempt |
| `homeassistant/event/keypad_entry` | Publish | Same payload, for HA automations |

### Event payload

```json
{
  "event_type": "keypad_code_entered",
  "device_id": "front-door",
  "user_id": "a1b2c3...",
  "user_name": "Jane Doe",
  "valid": true
}
```

For invalid codes, `event_type` is `keypad_invalid_code`, and `user_id`/`user_name` are omitted.

## Home Assistant automation example

Trigger an action whenever a valid code is entered:

```yaml
automation:
  - alias: "Keypad — valid entry"
    trigger:
      - platform: mqtt
        topic: homeassistant/event/keypad_entry
    condition:
      - condition: template
        value_template: "{{ trigger.payload_json.valid }}"
    action:
      - service: notify.mobile_app
        data:
          message: "{{ trigger.payload_json.user_name }} entered a valid code on {{ trigger.payload_json.device_id }}."
```

## REST API

The add-on exposes a JSON API alongside the web dashboard on port 8000.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/users` | List all registered users |
| `GET` | `/api/history?limit=50` | Recent entry history |

## Web dashboard

Open the dashboard via **Settings → Add-ons → Keypad Manager → Open Web UI**
or the **Keypad Manager** sidebar panel (if ingress is enabled).

From the dashboard you can:

- Add a user with a name and numeric PIN code.
- Remove an existing user.
- View the last 50 entry events with timestamps, device IDs, and pass/fail status.

## Data persistence

User records and entry history are stored as JSON files in the add-on's
persistent data volume (`/data/users.json` and `/data/history.json`).
They survive add-on restarts and updates.

## Changelog & Releases

Releases follow [Semantic Versioning][semver] (`MAJOR.MINOR.PATCH`):

- `MAJOR`: Breaking changes to configuration or MQTT topics.
- `MINOR`: New backwards-compatible features.
- `PATCH`: Bug fixes and dependency updates.

## Support

- Open an [issue on GitHub][issue] for bug reports or feature requests.
- [Home Assistant Community Forum][forum] for general questions.

## Authors & contributors

Created by [CJ Ramseyer][cjramseyer].

[contributors]: https://github.com/cjramseyer/keypad-app/graphs/contributors
[cjramseyer]: https://github.com/cjramseyer
[forum]: https://community.home-assistant.io
[issue]: https://github.com/cjramseyer/keypad-app/issues
[releases]: https://github.com/cjramseyer/keypad-app/releases
[semver]: https://semver.org

Copyright (c) 2024 CJ Ramseyer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[addon-badge]: https://my.home-assistant.io/badges/supervisor_addon.svg
[addon]: https://my.home-assistant.io/redirect/supervisor_addon/?addon=a0d7b954_example&repository_url=https%3A%2F%2Fgithub.com%2Fhassio-addons%2Frepository
[contributors]: https://github.com/hassio-addons/addon-example/graphs/contributors
[discord-ha]: https://discord.gg/c5DvZ4e
[discord]: https://discord.me/hassioaddons
[forum]: https://community.home-assistant.io/t/repository-community-hass-io-add-ons/24705?u=frenck
[cjramseyer]: https://github.com/cjramseyer
[issue]: https://github.com/hassio-addons/addon-example/issues
[reddit]: https://reddit.com/r/homeassistant
[releases]: https://github.com/hassio-addons/addon-example/releases
[semver]: http://semver.org/spec/v2.0.0.html