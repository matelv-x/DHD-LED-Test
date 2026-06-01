#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-/home/pi/sg1_v4}"

if [[ "$TARGET" == "--target" ]]; then
  TARGET="${2:-/home/pi/sg1_v4}"
fi

if [[ "$TARGET" == */web ]]; then
  echo "ERROR: Use sg1_v4 root folder, not /web."
  echo "Correct: sudo ./restore.sh /home/pi/sg1_v4"
  exit 1
fi

if [[ ! -d "$TARGET" ]]; then
  echo "ERROR: Target folder not found: $TARGET"
  exit 1
fi

BACKUP="${TARGET}_backup_before_dhd_test_restore_$(date +%Y%m%d_%H%M%S)"

echo "=== Creating safety backup ==="
cp -a "$TARGET" "$BACKUP"
echo "Backup created: $BACKUP"

echo "=== Removing DHD test hooks ==="
python3 - "$TARGET" <<'PY'
import re
import sys
from pathlib import Path

target = Path(sys.argv[1])

def read(path):
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        return handle.read()

def write(path, text):
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)

# keyboard_manager.py
km = target / "classes/keyboard_manager.py"
text = read(km)
text = re.sub(
    r"\n\s*# DHD TEST OVERLAY VARS START.*?"
    r"# DHD TEST OVERLAY VARS END\s*\n",
    "\n",
    text,
    flags=re.S,
)
text = re.sub(
    r"\n\s*# DHD TEST OVERLAY METHODS START.*?"
    r"# DHD TEST OVERLAY METHODS END\s*\n",
    "\n",
    text,
    flags=re.S,
)
text = re.sub(
    r"\n\s*# DHD TEST OVERLAY KEYPRESS START.*?"
    r"# DHD TEST OVERLAY KEYPRESS END\s*\n",
    "\n",
    text,
    flags=re.S,
)
write(km, text)
print("Cleaned:", km)

# web_server.py
ws = target / "classes/web_server.py"
text = read(ws)
text = re.sub(
    r"\n[ \t]*# DHD TEST OVERLAY LED ENDPOINT START.*?"
    r"# DHD TEST OVERLAY LED ENDPOINT END\r?\n\r?\n",
    "",
    text,
    flags=re.S,
)
text = re.sub(
    r"\n[ \t]*# DHD TEST OVERLAY ENABLE ENDPOINTS START.*?"
    r"# DHD TEST OVERLAY ENABLE ENDPOINTS END\r?\n\r?\n",
    "",
    text,
    flags=re.S,
)
text = re.sub(
    r'\n            elif self\.path == "/do/dhd_led_test":\n.*?'
    r'(?=\n            elif self\.path == "/do/dhd_test_enable":'
    r'|\n            elif self\.path == [\'"]/do/set_glyph_ring_zero[\'"]:'
    r'|\n            elif self\.path == "/do/clear_outgoing_buffer":)',
    "\n",
    text,
    count=1,
    flags=re.S,
)
write(ws, text)
print("Cleaned:", ws)

# debug.htm
debug = target / "web/debug.htm"
text = read(debug)
text = re.sub(
    r"[ \t]*<!-- DHD LED TEST UNIVERSAL PATCH START -->.*?"
    r"<!-- DHD LED TEST UNIVERSAL PATCH END -->\r?\n?",
    "",
    text,
    count=1,
    flags=re.S,
)
text = re.sub(
    r'\n\s*<button type="button" id="dhdLedTestButton" '
    r'class="btn-secondary controlButton">DHD LED Test<br>☏</button>',
    "",
    text,
    count=1,
)
write(debug, text)
print("Cleaned:", debug)
PY

echo "=== Removing DHD test files ==="
rm -f \
  "$TARGET/test/__init__.py" \
  "$TARGET/test/dhd_test.py" \
  "$TARGET/test/dhd_test_from_config.py"
rmdir "$TARGET/test" 2>/dev/null || true

echo "=== Syntax check ==="
python3 -m py_compile \
  "$TARGET/classes/keyboard_manager.py" \
  "$TARGET/classes/web_server.py"

echo "=== DHD TEST RESTORE COMPLETE ==="
echo "Restart with: sudo systemctl restart stargate.service"
