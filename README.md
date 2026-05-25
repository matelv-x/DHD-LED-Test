# DHD Test

Adds DHD LED browser test controls and backend test modes.

This repository is private while it is being checked and verified.

## Install

```bash
cd /home/pi/Stargate-Final_Patches
rm -rf DHD-Test
git clone https://github.com/matelv-x/DHD-Test.git
cd DHD-Test
chmod +x *.sh
sudo ./install.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## Restore / uninstall

```bash
cd /home/pi/Stargate-Final_Patches/DHD-Test
chmod +x restore.sh
sudo ./restore.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## What it changes

- Adds DHD ON/OFF and LED test controls to the debug page.
- Adds DHD test modes such as center, brightness, gradient, chase and strobe.
- Keeps firmware out of this package; this only patches the Pi software.

## Attribution and originality

Original base project: StargateProject SG1 software from the BuildAStargate/Jordan/Kristian/Jonnerd project lineage.

Additional source/idea credit: Built around the original DHD hardware/software behavior from the Kristian/Jonnerd StargateProject lineage.

How much is copied or changed: Medium patch. It modifies selected debug, keyboard and runtime files; it is not a firmware package.

The included `*.patch` file, when present, shows the exact text-level changes against the base software used while packaging.
