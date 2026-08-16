# Home Assistant Community Add-on: Keypad-App

[![GitHub Release][releases-shield]][releases]
![Project Stage][project-stage-shield]
[![License][license-shield]](LICENSE.md)

![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports i386 Architecture][i386-shield]

[![Github Actions][github-actions-shield]][github-actions]
![Project Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

Keypad management add-on for Home Assistant.

## About

Keypad Manager lets you register users with numeric PIN codes, listen for
keypad input over MQTT, and fire Home Assistant events on every code attempt.

**Key features:**

- Register unlimited users, each with a unique numeric PIN.
- Subscribes to `<prefix>/<device_id>/code` MQTT topics — works with any
  MQTT-capable keypad (Z-Wave via MQTT, Zigbee2MQTT, ESPHome, etc.).
- Publishes structured JSON events to `homeassistant/event/keypad_entry` for
  use in HA automations.
- Web dashboard (accessible via the HA sidebar) to manage users and browse
  the entry history log.
- JSON REST API at `/api/users` and `/api/history` for programmatic access.
- Auto-connects to the Home Assistant Mosquitto add-on; falls back to a
  manually configured broker.
- Persistent storage — user records and history survive restarts.

[:books: Read the full add-on documentation][docs]

## Support

Got questions?

You have several options to get them answered:

- The [Home Assistant Community Add-ons Discord chat server][discord] for add-on
  support and feature requests.
- The [Home Assistant Discord chat server][discord-ha] for general Home
  Assistant discussions and questions.
- The Home Assistant [Community Forum][forum].
- Join the [Reddit subreddit][reddit] in [/r/homeassistant][reddit]

You could also [open an issue here][issue] GitHub.

## Authors & contributors

Created and maintained by [CJ Ramseyer][cjramseyer].

For a full list of all contributors, see the [contributor's page][contributors].

## License

MIT License

Copyright (c) 2024-2026 CJ Ramseyer

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

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/cjramseyer/keypad-app.svg
[commits]: https://github.com/cjramseyer/keypad-app/commits/main
[contributors]: https://github.com/cjramseyer/keypad-app/graphs/contributors
[discord-ha]: https://discord.gg/c5DvZ4e
[discord-shield]: https://img.shields.io/discord/478094546522079232.svg
[discord]: https://discord.me/hassioaddons
[docs]: https://github.com/cjramseyer/keypad-app/blob/main/keypad-app/DOCS.md
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg
[forum]: https://community.home-assistant.io/t/repository-community-hass-io-add-ons/24705?u=frenck
[cjramseyer]: https://github.com/cjramseyer
[github-actions-shield]: https://github.com/cjramseyer/keypad-app/workflows/CI/badge.svg
[github-actions]: https://github.com/cjramseyer/keypad-app/actions
[github-sponsors-shield]: https://frenck.dev/wp-content/uploads/2019/12/github_sponsor.png
[github-sponsors]: https://github.com/sponsors/cjramseyer
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[issue]: https://github.com/cjramseyer/keypad-app/issues
[license-shield]: https://img.shields.io/github/license/cjramseyer/keypad-app.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2026.svg
[patreon-shield]: https://frenck.dev/wp-content/uploads/2019/12/patreon.png
[patreon]: https://www.patreon.com/cjramseyer
[project-stage-shield]: https://img.shields.io/badge/project%20stage-development-red.svg
[reddit]: https://reddit.com/r/homeassistant
[releases-shield]: https://img.shields.io/github/v/release/cjramseyer/keypad-app.svg
[releases]: https://github.com/cjramseyer/keypad-app/releases
[repository]: https://github.com/cjramseyer/keypad-app/repository