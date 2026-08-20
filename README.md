# Yardstick — Home Assistant integration

Brings your Yarbo into Home Assistant as a first-class **Yardstick** integration
— its own name and logo, auto-discovered, no cloud, no Yarbo account, nothing
that reaches the internet. It talks only to Yardstick running on your own
network, which in turn reads the robot locally.

## What you get

One **device per robot**, branded Yardstick, with live entities:

- **Battery** (%)
- **Activity** — Working / Standby / Charging / Returning to dock
- **RTK signal** — Fixed / Float / …
- **Fault code**
- **Online** and **Charging** (binary)

More (the robot on the map, controls) follows.

## Requirements

- Yardstick **0.7.21 or newer** running on your network, with an active licence.
- Home Assistant **2024.8** or newer.

## Install

### HACS (recommended once published)

Add this repository to HACS as a custom repository (category: Integration),
install **Yardstick**, and restart Home Assistant.

### Manually

Copy `custom_components/yardstick/` into your Home Assistant `config` folder so
you have `config/custom_components/yardstick/…`, then restart Home Assistant.

## Set it up

After restarting, Home Assistant should **discover Yardstick on its own** and
show *"Yardstick found — set up?"* under **Settings → Devices & Services**.
Accept it.

If it does not auto-discover (some networks block mDNS), add it by hand:
**Settings → Devices & Services → Add Integration → Yardstick**, and enter the
address of the computer running Yardstick (for example `192.168.1.250`, port
`8477`).

## Notes

- The integration is **read-only** for now and polls Yardstick every 15 seconds.
- If the Yardstick licence lapses, Home Assistant will say a licence is required.
