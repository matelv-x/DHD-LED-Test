# DHD LED Test

[![Downloads](https://img.shields.io/github/downloads/matelv-x/DHD-LED-Test/total?label=downloads)](https://github.com/matelv-x/DHD-LED-Test/releases)

DHD LED Test is a standalone add-on for the
[StargateProject-software](https://github.com/jonnerd154/StargateProject-software)
project by jonnerd154.

## What it does

DHD LED Test provides the ability to test the DHD LEDs using seven different
test modes:

- Full Suite
- Center Pixel Only
- Brightness Sweep
- Rainbow Gradient
- Ring Chase
- Random Strobe
- Individual LED Test

This is a completely separate test system from the one originally included in
the image provided by the project author.

## Install

Method — GitHub Clone (Recommended)

```bash
cd /home/pi
rm -rf DHD-Test DHD-LED-Test DHD-LED-Test-main
git clone https://github.com/matelv-x/DHD-LED-Test.git
cd DHD-LED-Test
chmod +x install.sh restore.sh
sudo ./install.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## Restore / uninstall

```bash
cd /home/pi/DHD-LED-Test
chmod +x restore.sh
sudo ./restore.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## What it changes

- Adds DHD test files under `test/`.
- Injects only the required hooks into `classes/keyboard_manager.py`,
  `classes/web_server.py`, and `web/debug.htm`.
- Surgical restore removes only DHD LED Test files and DHD LED Test hooks.
- Preserves the original SG1 DHD Test controls already included in the base image.
- Creates a full SG1 backup before installation and before surgical restore.
- Installer targets `/home/pi/sg1_v4`.

## Attribution and originality,

Author: matelv-x.

This add-on is designed to work with the StargateProject-software project.
