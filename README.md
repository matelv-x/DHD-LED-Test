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
chmod +x install.sh
sudo ./install.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## Restore / uninstall

```bash
Restore from the backup path printed by the installer, or restore the SG1 v4 folder from a known-good backup.
```

## What it changes

- Adds DHD test files under `test/`.
- Installer targets `/home/pi/sg1_v4`.
- Use current `DHD_Test.zip` version, not old `dhd_test.v1.zip`.

## Attribution and originality

Original base project: StargateProject SG1 software from the BuildAStargate/Jordan/Kristian/Jonnerd project lineage.

Additional source/idea credit: DHD behavior comes from the original StargateProject hardware/software lineage; packaging by Marcin/Codex.

How much is copied or changed: Small helper package.
