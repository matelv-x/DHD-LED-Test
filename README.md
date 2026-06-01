# DHD Test

DHD test helper package from the final-patches folder.

This repository is private while it is being checked and verified.

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
- Surgical restore removes only DHD Test files and DHD Test hooks.
- Preserves the original SG1 DHD Test controls already included in the base image.
- Creates a full SG1 backup before installation and before surgical restore.
- Installer targets `/home/pi/sg1_v4`.
- Use current `DHD_Test.zip` version, not old `dhd_test.v1.zip`.

## Attribution and originality

Original base project: StargateProject SG1 software from the BuildAStargate/Jordan/Kristian/Jonnerd project lineage.

Additional source/idea credit: DHD behavior comes from the original StargateProject hardware/software lineage; packaging by matelv-x/Codex.

How much is copied or changed: Small helper package.
