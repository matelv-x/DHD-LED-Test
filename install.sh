#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-/home/pi/sg1_v4}"

if [[ "$TARGET" == "--target" ]]; then
  TARGET="${2:-/home/pi/sg1_v4}"
fi

if [[ "$TARGET" == */web ]]; then
  echo "ERROR: Use sg1_v4 root folder, not /web."
  echo "Correct: sudo ./install.sh /home/pi/sg1_v4"
  exit 1
fi

if [[ ! -d "$TARGET" ]]; then
  echo "ERROR: Target folder not found: $TARGET"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP="${TARGET}_backup_dhd_test_universal_$(date +%Y%m%d_%H%M%S)"

echo "=== Creating backup ==="
cp -a "$TARGET" "$BACKUP"
echo "Backup created: $BACKUP"

echo "=== Installing DHD test files ==="
mkdir -p "$TARGET/test"
cp "$SCRIPT_DIR/files/test/__init__.py" "$TARGET/test/__init__.py"
cp "$SCRIPT_DIR/files/test/dhd_test.py" "$TARGET/test/dhd_test.py"
cp "$SCRIPT_DIR/files/test/dhd_test_from_config.py" "$TARGET/test/dhd_test_from_config.py"

echo "=== Injecting universal DHD test hooks ==="
python3 - "$TARGET" <<'PY'
import re
import sys
from pathlib import Path

target = Path(sys.argv[1])

def read(p):
    with p.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        return handle.read()

def write(p, s):
    with p.open("w", encoding="utf-8", newline="") as handle:
        handle.write(s)

# keyboard_manager.py
km = target / "classes/keyboard_manager.py"
s = read(km)

if "self.dhd_test_enable" not in s:
    marker = "self.symbol_manager = stargate.symbol_manager"
    if marker in s:
        s = s.replace(marker, marker + """

        # DHD TEST OVERLAY VARS START
        self.dhd_test_enable = False
        self.dhd_test_active_buttons = []
        # DHD TEST OVERLAY VARS END""", 1)
    else:
        print("WARNING: Could not inject DHD test vars into keyboard_manager.py")

methods = """
    # DHD TEST OVERLAY METHODS START
    def enable_dhd_test(self, enable):
        if enable:
            try:
                self.stargate.shutdown()
            except Exception:
                pass
            self.dhd_test_enable = True
            self.log.log("DHD Test Mode: enabled")
        else:
            self.dhd_test_enable = False
            try:
                self.stargate.dialer.hardware.clear_lights()
            except Exception:
                pass
            self.log.log("DHD Test Mode: disabled")

        self.dhd_test_active_buttons = []

    def handle_dhd_test(self, key):
        raw = str(key).strip()
        center = str(getattr(self, "center_button_key", "A")).strip()

        if raw == center:
            try:
                self.stargate.dialer.hardware.set_center_on()
                self.log.log("DHD Test: CENTER pressed -> set_center_on()")
            except Exception as exc:
                self.log.log(f"DHD Test: center LED error: {exc}")
            return

        try:
            symbol_number = self.symbol_manager.get_symbol_key_map()[key]
            self.log.log(f"DHD Test: Pressed Key {key} --> Symbol {symbol_number}")
        except KeyError:
            self.log.log(f"DHD Test: Key NOT RECOGNIZED {key}")
            return

        try:
            if symbol_number not in self.dhd_test_active_buttons:
                self.dhd_test_active_buttons.append(symbol_number)
                self.stargate.dialer.hardware.set_pixel(symbol_number, 250, 117, 0)
                self.stargate.dialer.hardware.latch()
            else:
                self.dhd_test_active_buttons.remove(symbol_number)
                self.stargate.dialer.hardware.clear_pixel(symbol_number)
                self.stargate.dialer.hardware.latch()
        except Exception as exc:
            self.log.log(f"DHD Test: LED error for symbol {symbol_number}: {exc}")

    # DHD TEST OVERLAY METHODS END
"""

if "def handle_dhd_test" not in s:
    idx = s.find("    def keypress_handler")
    if idx != -1:
        s = s[:idx] + methods + "\n" + s[idx:]
    else:
        print("WARNING: Could not inject DHD test methods into keyboard_manager.py")

if "if self.dhd_test_enable:" not in s:
    s = re.sub(
        r'(    def keypress_handler\( self, key \):[\s\S]*?"""\s*\n)',
        r'\1\n        # DHD TEST OVERLAY KEYPRESS START\n        if getattr(self, "dhd_test_enable", False):\n            self.handle_dhd_test(key)\n            return\n        # DHD TEST OVERLAY KEYPRESS END\n',
        s,
        count=1
    )

write(km, s)
print("Patched:", km)

# web_server.py
ws = target / "classes/web_server.py"
s = read(ws)

endpoint = """
            # DHD TEST OVERLAY LED ENDPOINT START
            elif self.path == "/do/dhd_led_test":
                try:
                    dhd = getattr(self.stargate.dialer, "hardware", None)
                    dhd_type = getattr(self.stargate.dialer, "type", "Unknown")

                    if dhd is None or dhd_type != "DHDv2":
                        self.stargate.log.log(f"DHD LED TEST: DHD not active (type={dhd_type})")
                        data = {
                            "success": False,
                            "message": "DHDv2 not connected"
                        }
                    else:
                        try:
                            mode = data.get("mode", "full")
                        except Exception:
                            mode = "full"

                        from test.dhd_test_from_config import dhd_led_test_backend
                        import threading

                        threading.Thread(
                            target=dhd_led_test_backend.run_dhd_test,
                            args=(dhd, self.stargate.log, mode),
                            daemon=True
                        ).start()

                        data = {"success": True, "mode": mode}

                except Exception as exc:
                    self.stargate.log.log(f"DHD LED TEST ERROR: {exc}")
                    data = {"success": False, "message": str(exc)}
            # DHD TEST OVERLAY LED ENDPOINT END

"""

if "/do/dhd_led_test" not in s:
    inserted = False
    for marker in ['            elif self.path == "/do/set_glyph_ring_zero":', "            elif self.path == '/do/set_glyph_ring_zero':", '            elif self.path == "/do/clear_outgoing_buffer":']:
        if marker in s:
            s = s.replace(marker, endpoint + marker, 1)
            inserted = True
            break
    if not inserted:
        print("WARNING: Could not insert /do/dhd_led_test endpoint")

enable_block = """
            # DHD TEST OVERLAY ENABLE ENDPOINTS START
            elif self.path == "/do/dhd_test_enable":
                try:
                    self.stargate.keyboard.enable_dhd_test(True)
                    data = {"success": True}
                except Exception as exc:
                    self.stargate.log.log(f"DHD TEST ENABLE ERROR: {exc}")
                    data = {"success": False, "message": str(exc)}

            elif self.path == "/do/dhd_test_disable":
                try:
                    self.stargate.keyboard.enable_dhd_test(False)
                    data = {"success": True}
                except Exception as exc:
                    self.stargate.log.log(f"DHD TEST DISABLE ERROR: {exc}")
                    data = {"success": False, "message": str(exc)}
            # DHD TEST OVERLAY ENABLE ENDPOINTS END

"""

if "/do/dhd_test_enable" not in s:
    inserted = False
    for marker in ['            elif self.path == "/do/set_glyph_ring_zero":', "            elif self.path == '/do/set_glyph_ring_zero':", '            elif self.path == "/do/clear_outgoing_buffer":']:
        if marker in s:
            s = s.replace(marker, enable_block + marker, 1)
            inserted = True
            break
    if not inserted:
        print("WARNING: Could not insert /do/dhd_test_enable endpoints")

write(ws, s)
print("Patched:", ws)

# debug.htm
dh = target / "web/debug.htm"
s = read(dh)

s = re.sub(
    r'[ \t]*<!-- DHD LED TEST UNIVERSAL PATCH START -->.*?'
    r'<!-- DHD LED TEST UNIVERSAL PATCH END -->\r?\n?',
    '',
    s,
    flags=re.S
)

button = '<button type="button" id="dhdLedTestButton" class="btn-secondary controlButton">DHD LED Test<br>☏</button>'

if "dhdLedTestButton" not in s:
    marker = "<h4>Dial Home Device</h4>"
    if marker in s:
        s = s.replace(marker, marker + "\n        " + button, 1)
    else:
        s = s.replace("</div>\n    </main>", '        <hr />\n        <h4>Dial Home Device</h4>\n        ' + button + '\n      </div>\n    </main>', 1)

if 'action="dhd_test_enable"' not in s and button in s:
    s = s.replace(
        button,
        button + '\n        <button type="button" class="btn-secondary controlButton" action="dhd_test_enable">Test Mode<br>Enable</button>\n        <button type="button" class="btn-secondary controlButton" action="dhd_test_disable">Test Mode<br>Disable</button>',
        1
    )

script = """
<!-- DHD LED TEST UNIVERSAL PATCH START -->
<script type="text/javascript">
  function runDhdTest(mode) {
    $.post({
      url: 'stargate/do/dhd_led_test',
      data: JSON.stringify({ mode: mode }),
      contentType: 'application/json'
    })
    .done(function(response) {
      var $startedDialog = $("<div>DHD LED test '" + mode + "' started. Check logs.</div>").dialog({
        modal: false
      });
      setTimeout(function() {
        $startedDialog.dialog('close');
        $startedDialog.remove();
      }, 2000);
    })
    .fail(function() {
      $("<div>Failed to start DHD LED test.</div>").dialog();
    });
  }

  function openDhdTestDialog() {
    var $dlg = $('<div title="Select DHD LED test">' +
      '<p>Choose which DHD LED test you want to run:</p>' +
      '<button class="dhdTestChoice" data-mode="full">Full suite</button><br>' +
      '<button class="dhdTestChoice" data-mode="center">Center pixel only</button><br>' +
      '<button class="dhdTestChoice" data-mode="brightness">Brightness sweep</button><br>' +
      '<button class="dhdTestChoice" data-mode="gradient">Rainbow gradient</button><br>' +
      '<button class="dhdTestChoice" data-mode="ring_chase">Ring chase</button><br>' +
      '<button class="dhdTestChoice" data-mode="random_strobe">Random strobe</button><br>' +
      '<button class="dhdTestChoice" data-mode="individual">Individual LED test</button>' +
      '</div>');

    $dlg.on('click', '.dhdTestChoice', function() {
      var mode = $(this).data('mode');
      $dlg.dialog('close');
      runDhdTest(mode);
    });

    $dlg.dialog({
      modal: true,
      width: 350
    });
  }

  $(function() {
    $('#dhdLedTestButton')
      .off('click')
      .off('click.dhdUniversal')
      .on('click.dhdUniversal', function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        openDhdTestDialog();
        return false;
      });
  });
</script>
<!-- DHD LED TEST UNIVERSAL PATCH END -->
"""

newline = "\r\n" if "\r\n" in s else "\n"
script = script.strip("\n").replace("\n", newline)

if re.search(r"(?m)^[ \t]*</body>", s):
    s = re.sub(
        r"(?m)^[ \t]*</body>",
        lambda match: script + newline + match.group(0),
        s,
        count=1,
    )
else:
    s += newline + script + newline

write(dh, s)
print("Patched:", dh)

PY

echo "=== Syntax check ==="
python3 -m py_compile \
  "$TARGET/classes/keyboard_manager.py" \
  "$TARGET/classes/web_server.py" \
  "$TARGET/test/dhd_test.py" \
  "$TARGET/test/dhd_test_from_config.py"

echo "=== Done ==="
echo "Restart with: sudo systemctl restart stargate.service"
echo "Surgical restore with: sudo ./restore.sh $TARGET"
echo "Emergency full backup restore with: sudo rsync -a --delete $BACKUP/ $TARGET/"
