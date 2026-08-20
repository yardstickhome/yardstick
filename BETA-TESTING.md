# Yardstick for Home Assistant — beta tester guide

This connects your Yarbo to Home Assistant through Yardstick, entirely on your
own network. No Yarbo account, no cloud. You get live readings, and (if you
choose) full control: start a plan, pause, dock, blades, lights, and more.

## Before you start

You need three things:

1. **Yardstick running** on your network, on this beta build or newer, with an
   active licence or trial. Home Assistant reads Yardstick, so Yardstick has to
   be up. Note the computer's IP address (the one you open Yardstick on).
2. **Home Assistant** on the same network.
3. **Only if you want control** (not just reading): open Yardstick's Settings and
   turn **Manual control** on. That is the single safety switch. With it off, Home
   Assistant can read everything but cannot move the machine. Your call, your yard.

## Step 1 — Install the integration

**Option A, HACS (recommended):**
1. In Home Assistant, open **HACS**.
2. Top-right ⋮ → **Custom repositories**.
3. Paste the repository URL: `https://github.com/<ORG>/<REPO>` (we will give you
   this), category **Integration**, and click **Add**.
4. Find **Yardstick** in the list and **Download** it.
5. **Restart Home Assistant** (Settings → System → Restart).

**Option B, manual (no HACS):**
1. Copy the `custom_components/yardstick` folder into your Home Assistant
   `config/custom_components/` folder.
2. **Restart Home Assistant.**

## Step 2 — Add it

After the restart, Home Assistant may pop up **"Yardstick discovered"** on its
own (it advertises over the network). If it does, click **Configure**. If not:

1. Settings → **Devices & Services** → **+ Add Integration**.
2. Search **Yardstick**.
3. Enter:
   - **Host:** the IP address of the computer running Yardstick
   - **Port:** `8477`
4. Submit. You now have a **Yarbo** device.

## Step 3 — See it working

Open the Yarbo device (Settings → Devices & Services → Yardstick → your Yarbo).
You will have:

- **Sensors:** battery, activity, RTK signal, fault code, online, charging
- **Mower** (`lawn_mower.yarbo`): Start, Pause, Dock
- **Plan** selector: which saved plan "Start" runs
- **Buttons:** Send home, Pause, Resume, Stop, Find (sound)
- **Switches:** Blades, Lights, Camera
- **Numbers:** Blower speed, Blade height, Head lift, Chute angle

To put a control card on a dashboard: Overview → ⋮ **Edit dashboard** → **+ Add
card** → search **Yarbo** → add the mower entity (and the Plan selector next to it).

## Step 4 — Start a plan from Home Assistant

1. Set the **Plan** selector to the plan you want.
2. Press **Start** on the mower card.

If the Plan selector is empty, the robot was asleep when Home Assistant loaded.
Reload the integration (Yardstick → ⋮ → **Reload**) while the robot is awake.

## Automations

Anything in Home Assistant can now trigger the Yarbo. For example, mow the front
when the garage opens:

```yaml
alias: Mow the front yard when the garage opens
triggers:
  - trigger: state
    entity_id: cover.garage_door
    to: "open"
actions:
  - action: select.select_option
    target:
      entity_id: select.yarbo_plan
    data:
      option: "Front yard"
  - action: lawn_mower.start_mowing
    target:
      entity_id: lawn_mower.yarbo
```

## If something is off

- **"Needs an active licence":** Home Assistant needs Yardstick to be licensed or
  in trial. Paste your key into Yardstick's Setup.
- **Controls do nothing / "Manual control is switched off":** turn Manual control
  on in Yardstick's Settings.
- **No entities after adding:** make sure you restarted Home Assistant after
  installing, and that Yardstick is reachable at the host and port you entered.
- **Plan list empty:** the robot was asleep; wake it and reload the integration.

## Tell us

This is a beta. If an entity looks wrong, a control does not do what you expect,
or setup snags, send it to support@yardstickhome.com or open a ticket at
yardstickhome.com/support. Include what your robot was doing at the time.
