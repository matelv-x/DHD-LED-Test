# DHD LED Test

DHD LED Test is a standalone add-on for the
[StargateProject-software](https://github.com/jonnerd154/StargateProject-software)
project by jonnerd154.

This repository is private while it is being checked and verified.

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

Clone or unzip this add-on into `/home/pi`, then run:

```bash
cd /home/pi
rm -rf DHD-Test
git clone https://github.com/matelv-x/DHD-Test.git
cd DHD-Test
chmod +x install.sh restore.sh
sudo ./install.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## Restore / uninstall

```bash
cd /home/pi/DHD-Test
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

## Attribution and originality

Author: matelv-x.

DHD LED Test is an original standalone add-on created by matelv-x.

No feature, behavior, modification, or implementation in this add-on was copied
or derived from another add-on idea.

This add-on is designed to work with the StargateProject-software project, but
it remains a separate matelv-x add-on.
