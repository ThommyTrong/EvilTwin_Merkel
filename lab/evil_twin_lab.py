#!/usr/bin/env python3

"""
Virtuelle Evil-Twin-Labor-Demo direkt auf Kali/Linux (ohne Mininet-WiFi).

Nutzt ausschließlich das Kernel-Modul mac80211_hwsim + Linux Network Namespaces.
Es werden keine realen Funkframes nach außen gesendet.

Aufbau:
- Namespace 'et_legit' : Campus-AP  (SSID: Seminar-Gast, BSSID: 02:00:00:00:00:11) + HTTP 10.0.0.1:8080
- Namespace 'et_evil'  : Evil Twin  (SSID: Seminar-Gast, BSSID: 02:00:00:00:00:22) + HTTP 10.0.0.1:8080
- Namespace 'et_client': Test-Client (MAC: 02:00:00:00:00:99, IP: 10.0.0.10/24)
"""

import argparse
import os
import pwd
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SSID = "Seminar-Gast"
PASSWD = "LabTest-2026"
BSSID_REAL = "02:00:00:00:00:11"
BSSID_EVIL = "02:00:00:00:00:22"
MAC_CLIENT = "02:00:00:00:00:99"

NS_LEGIT = "et_legit"
NS_EVIL = "et_evil"
NS_CLIENT = "et_client"
CTRL_DIR = "/run/wpa_supplicant_etlab"

PAGE_STYLE = """
<style>
:root{font-family:Inter,Arial,sans-serif;color:#17202a;background:#eef1f4}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:32px}
.shell{width:min(760px,100%);background:#fff;border-radius:24px;overflow:hidden;box-shadow:0 24px 70px #17202a24}
.top{padding:22px 28px;color:#fff;background:#626b73;display:flex;align-items:center;gap:14px}
.mark{font-weight:900;font-size:22px;letter-spacing:.06em}.evil .top{background:#a90016}
.body{padding:34px}.eyebrow{margin:0 0 8px;color:#e2001a;font-weight:800;letter-spacing:.08em;font-size:13px}
h1{margin:0 0 10px;font-size:34px;line-height:1.1}p{line-height:1.55;color:#5b6470}
.facts{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:26px 0}
.fact{padding:15px;border:1px solid #dde1e5;border-radius:14px;background:#f7f8f9}
.fact b{display:block;font-size:12px;color:#6a727b;margin-bottom:5px}.fact code{font-size:15px}
.button{display:block;width:100%;border:0;border-radius:12px;padding:16px;background:#5b6470;color:#fff;font-size:16px;font-weight:700;text-align:center}
.evil .button{background:#e2001a}.notice{margin-top:20px;padding:15px 18px;border-radius:12px;background:#fdecee;color:#7f1321;font-size:14px}
.safe{background:#e9f5ed;color:#17633a}.footer{padding:16px 28px;border-top:1px solid #e3e6e9;font-size:12px;color:#727b84}
.nav{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 6px}
.nav a{padding:8px 13px;border-radius:10px;background:#eef1f4;color:#17202a;text-decoration:none;font-size:13px;font-weight:700}
.nav a:hover{background:#dde1e5}
.evil .nav a{background:#fdecee;color:#7f1321}
@media(max-width:600px){.facts{grid-template-columns:1fr}.body{padding:24px}h1{font-size:28px}}
</style>
"""

NAV_HTML = """
    <nav class="nav">
      <a href="/">Startseite</a>
      <a href="/stundenplan">Stundenplan</a>
      <a href="/mensa">Mensa-Plan</a>
      <a href="/news">Campus-News</a>
    </nav>
"""

LEGIT_PAGE = f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Campus-Portal</title>{PAGE_STYLE}</head>
<body><main class="shell">
  <header class="top"><span class="mark">DHBW</span><b>Lörrach · Campus-Gastzugang</b></header>
  <section class="body">
    <p class="eyebrow">LEGITIMER ACCESS POINT (ROUTER 1)</p>
    <h1>Du bist mit dem Campus-Netz verbunden.</h1>
    <p>Der Demonstrationszugang zeigt die harmlose Zielseite des echten Access Points. Klicke unten auf einen Link, um im Router-Log zu sehen, was dein Client aufruft.</p>
    <div class="facts">
      <div class="fact"><b>Netzwerk</b><code>{SSID}</code></div>
      <div class="fact"><b>Verbunden mit BSSID</b><code>{BSSID_REAL}</code></div>
    </div>
{NAV_HTML}
    <span class="button">Internetfreigabe · Demo</span>
    <div class="notice safe"><b>Keine Anmeldung nötig.</b> Es werden keine Daten abgefragt oder gespeichert.</div>
  </section>
  <footer class="footer">Virtuelles Labor · mac80211_hwsim · kein reales Funksignal</footer>
</main></body></html>"""

EVIL_PAGE = f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Portal · Seminar-Gast</title>{PAGE_STYLE}</head>
<body><main class="shell evil">
  <header class="top"><span class="mark">WLAN</span><b>Seminar-Gast · Verbindungsprüfung</b></header>
  <section class="body">
    <p class="eyebrow">SIMULIERTES EVIL-TWIN-PORTAL (ROUTER 2)</p>
    <h1>Das Netzwerk heißt gleich. Der Betreiber nicht.</h1>
    <p>Diese Seite gehört zum zweiten virtuellen Access Point. Klicke unten auf einen Link: Router 2 protokolliert jetzt jede Anfrage deines Browsers.</p>
    <div class="facts">
      <div class="fact"><b>Identische SSID</b><code>{SSID}</code></div>
      <div class="fact"><b>Andere BSSID</b><code>{BSSID_EVIL}</code></div>
    </div>
{NAV_HTML}
    <span class="button">Anmeldefeld absichtlich gesperrt</span>
    <div class="notice"><b>Demo-Schutz aktiv:</b> Es existiert kein Formular und es werden keinerlei Zugangsdaten angenommen oder gespeichert.</div>
  </section>
  <footer class="footer">Präsentationssimulation · Sie zeigt das Risiko, ohne Credentials zu sammeln</footer>
</main></body></html>"""

ROUTER_HTTP_SCRIPT = """import datetime, http.server, pathlib, sys

router_name, directory, logfile = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
index_bytes = (directory / "index.html").read_bytes()

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        ua = self.headers.get("User-Agent", "-")
        line = f"[{ts}] [{router_name}] {self.client_address[0]} -> GET {self.path} | UA: {ua[:48]}\\n"
        with logfile.open("a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(index_bytes)))
        self.end_headers()
        self.wfile.write(index_bytes)

    def log_message(self, format, *args):
        return

http.server.ThreadingHTTPServer(("10.0.0.1", 8080), Handler).serve_forever()
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Virtuelle Evil-Twin-Demo mit mac80211_hwsim (Kali/Linux)."
    )
    parser.add_argument(
        "--mode",
        choices=("wpa2", "wpa3", "open"),
        default="wpa2",
        help="Sicherheitsmodus der virtuellen APs (Standard: wpa2).",
    )
    return parser.parse_args()


def run(cmd, check=True, capture=False):
    return subprocess.run(
        cmd,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


def ns_cmd(ns, *args, check=True, capture=False):
    return run(["ip", "netns", "exec", ns, *args], check=check, capture=capture)


def check_dependencies():
    needed = ["ip", "iw", "hostapd", "wpa_supplicant", "wpa_cli", "curl"]
    missing = [tool for tool in needed if shutil.which(tool) is None]
    if missing:
        sys.exit(
            f"Fehlende Tools: {', '.join(missing)}\n"
            "Installieren mit:\n"
            "  sudo apt update && sudo apt install -y hostapd wpasupplicant iw iproute2 curl"
        )


def hwsim_phys():
    base = Path("/sys/devices/virtual/mac80211_hwsim")
    if not base.exists():
        return []
    phys = []
    for hw in sorted(base.glob("hwsim*")):
        for phy in sorted((hw / "ieee80211").glob("phy*")):
            phys.append(phy.name)
    return phys


def iface_in_ns(ns):
    out = ns_cmd(ns, "ls", "/sys/class/net", capture=True).stdout.split()
    ifaces = [i for i in out if i != "lo"]
    if not ifaces:
        raise RuntimeError(f"Kein WLAN-Interface im Namespace {ns} gefunden.")
    return ifaces[0]


def write_hostapd_conf(path, iface, bssid, channel, mode):
    lines = [
        f"interface={iface}",
        "driver=nl80211",
        f"ssid={SSID}",
        f"bssid={bssid}",
        "hw_mode=g",
        f"channel={channel}",
        "auth_algs=1",
    ]
    if mode == "wpa2":
        lines += [
            "wpa=2",
            f"wpa_passphrase={PASSWD}",
            "wpa_key_mgmt=WPA-PSK",
            "rsn_pairwise=CCMP",
            "ieee80211w=0",
        ]
    elif mode == "wpa3":
        lines += [
            "wpa=2",
            f"wpa_passphrase={PASSWD}",
            "wpa_key_mgmt=SAE",
            "rsn_pairwise=CCMP",
            "ieee80211w=2",
            "sae_pwe=2",
        ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_wpa_conf(path, mode):
    lines = [
        f"ctrl_interface={CTRL_DIR}",
        "update_config=0",
        "network={",
        f'    ssid="{SSID}"',
    ]
    if mode == "open":
        lines.append("    key_mgmt=NONE")
    elif mode == "wpa2":
        lines += [
            "    key_mgmt=WPA-PSK",
            f'    psk="{PASSWD}"',
            "    ieee80211w=0",
        ]
    elif mode == "wpa3":
        lines += [
            "    key_mgmt=SAE",
            f'    psk="{PASSWD}"',
            "    ieee80211w=2",
        ]
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cleanup(procs, tmpdir):
    print("\n[*] Räume virtuelle Laborumgebung auf...")
    for proc in procs:
        if proc.poll() is None:
            proc.terminate()
    time.sleep(0.5)
    for proc in procs:
        if proc.poll() is None:
            proc.kill()
    for ns in (NS_CLIENT, NS_EVIL, NS_LEGIT):
        run(["ip", "netns", "del", ns], check=False, capture=True)
    run(["modprobe", "-r", "mac80211_hwsim"], check=False, capture=True)
    shutil.rmtree(CTRL_DIR, ignore_errors=True)
    shutil.rmtree(tmpdir, ignore_errors=True)
    print("[*] Fertig.")


def wait_connected(if_client, timeout=8.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        out = ns_cmd(NS_CLIENT, "iw", "dev", if_client, "link", check=False, capture=True).stdout
        if "Connected to" in out:
            return
        time.sleep(0.4)


def show_status(if_client):
    print(f"\n$ ip netns exec {NS_CLIENT} iw dev {if_client} link")
    print(ns_cmd(NS_CLIENT, "iw", "dev", if_client, "link", check=False, capture=True).stdout.strip())
    print(f"\n$ ip netns exec {NS_CLIENT} curl -s http://10.0.0.1:8080")
    out = ns_cmd(NS_CLIENT, "curl", "-s", "--max-time", "3", "http://10.0.0.1:8080", check=False, capture=True).stdout
    print(out.strip() or "(Keine Antwort — ggf. kurz warten und erneut probieren)")


def show_scan(if_client):
    print(f"\n$ ip netns exec {NS_CLIENT} iw dev {if_client} scan | grep -E 'BSS|SSID|signal'")
    out = ns_cmd(NS_CLIENT, "iw", "dev", if_client, "scan", check=False, capture=True).stdout
    for line in out.splitlines():
        s = line.strip()
        if s.startswith(("BSS ", "SSID:", "signal:")):
            print(" ", line)


def show_packet_trace():
    if shutil.which("tshark") is None:
        print("\n[!] tshark ist nicht installiert. Paketansicht überspringen.")
        return
    run(["ip", "link", "set", "hwsim0", "up"], check=False, capture=True)
    print("\n[*] Erfasse 8 Sekunden virtuelle 802.11-Frames (nur lokal in mac80211_hwsim)...")
    result = run(
        [
            "tshark",
            "-i",
            "hwsim0",
            "-a",
            "duration:8",
            "-n",
            "-Y",
            "wlan.fc.type_subtype == 0x0008 || wlan.fc.type == 2",
            "-T",
            "fields",
            "-e",
            "frame.time_relative",
            "-e",
            "wlan.sa",
            "-e",
            "wlan.da",
            "-e",
            "wlan.fc.type_subtype",
            "-e",
            "frame.len",
        ],
        check=False,
        capture=True,
    )
    output = (result.stdout or "").strip()
    print(output or "[!] In diesem Zeitraum wurden keine passenden Frames angezeigt.")


def browser_environment():
    username = os.environ.get("SUDO_USER")
    if not username or username == "root":
        return None
    user = pwd.getpwnam(username)
    env = {
        "HOME": user.pw_dir,
        "USER": username,
        "LOGNAME": username,
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    }
    for key in ("DISPLAY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS"):
        if os.environ.get(key):
            env[key] = os.environ[key]
    return username, env


def open_portal():
    browser = os.environ.get("EVILTWIN_BROWSER")
    candidates = [browser] if browser else ["firefox-esr", "firefox", "chromium"]
    executable = next((item for item in candidates if item and shutil.which(item)), None)
    identity = browser_environment()
    if executable is None:
        print(
            "\n[!] Kein Browser gefunden. Öffne im Kali-Gast manuell:\n"
            "  http://10.0.0.1:8080\n"
            "Hinweis: Der Browser muss im Namespace et_client laufen."
        )
        return
    if identity is None:
        print(
            f"\n[!] Starte die Demo mit sudo und öffne danach in einem zweiten Terminal:\n"
            f"  sudo ip netns exec {NS_CLIENT} {executable} http://10.0.0.1:8080"
        )
        return
    username, env = identity
    try:
        subprocess.Popen(
            [
                "ip",
                "netns",
                "exec",
                NS_CLIENT,
                "sudo",
                "-u",
                username,
                "env",
                *[f"{key}={value}" for key, value in env.items()],
                executable,
                "--new-window",
                "http://10.0.0.1:8080",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        print("\n[*] Browser im virtuellen Client-Netzwerk geöffnet.")
    except OSError as exc:
        print(f"\n[!] Browser konnte nicht gestartet werden: {exc}")


def show_router_view(if_legit, if_evil, legit_log, evil_log, evil_started):
    print("\n=== Router-Sicht: Verbundene Clients & HTTP-Log ===")
    for label, ns, iface, log_path, active in (
        (f"ROUTER 1 (Legitimer AP {BSSID_REAL})", NS_LEGIT, if_legit, legit_log, True),
        (f"ROUTER 2 (Evil Twin   {BSSID_EVIL})", NS_EVIL, if_evil, evil_log, evil_started),
    ):
        print(f"\n--- {label} ---")
        if not active:
            print("  Status: Noch nicht gestartet (erst [3] oder [4] wählen).")
            continue
        st = ns_cmd(ns, "iw", "dev", iface, "station", "dump", check=False, capture=True).stdout.strip()
        if "Station " in st:
            for line in st.splitlines():
                s = line.strip()
                if s.startswith(("Station ", "rx packets:", "tx packets:", "signal:")):
                    print(" ", s)
        else:
            print("  Verbundene Clients: (keiner)")
        lines = log_path.read_text(encoding="utf-8").splitlines() if log_path.exists() else []
        print("  Letzte HTTP-Anfragen an diesen Router:")
        if lines:
            for line in lines[-8:]:
                print("   ", line)
        else:
            print("    (noch keine Anfragen)")


def live_router_monitor(legit_log, evil_log):
    print("\n=== Live-Monitor: Traffic auf Router 1 (:11) & Router 2 (:22) ===")
    print("Klicke im Browser auf Links oder öffne Seiten. Beenden mit Strg+C.\n")
    pos = {legit_log: legit_log.stat().st_size if legit_log.exists() else 0,
           evil_log: evil_log.stat().st_size if evil_log.exists() else 0}
    try:
        while True:
            for path in (legit_log, evil_log):
                if not path.exists():
                    continue
                size = path.stat().st_size
                if size > pos[path]:
                    with path.open("r", encoding="utf-8") as f:
                        f.seek(pos[path])
                        chunk = f.read()
                    pos[path] = size
                    for line in chunk.splitlines():
                        print(" ", line)
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("\n[*] Live-Monitor beendet, zurück zum Menü.")


def roam_client(if_client, target_bssid):
    print(f"\n$ ip netns exec {NS_CLIENT} wpa_cli -p {CTRL_DIR} -i {if_client} roam {target_bssid}")
    res = ns_cmd(NS_CLIENT, "wpa_cli", "-p", CTRL_DIR, "-i", if_client, "roam", target_bssid, check=False, capture=True)
    print(" ", res.stdout.strip())
    time.sleep(2)
    ns_cmd(NS_CLIENT, "ip", "neigh", "flush", "dev", if_client, check=False, capture=True)
    show_status(if_client)


def main():
    args = parse_args()
    if os.geteuid() != 0:
        sys.exit("Bitte mit sudo ausführen: sudo python3 lab/evil_twin_lab.py")
    check_dependencies()

    tmpdir = Path(tempfile.mkdtemp(prefix="eviltwin_lab_"))
    legit_dir = tmpdir / "legit"
    evil_dir = tmpdir / "evil"
    legit_dir.mkdir()
    evil_dir.mkdir()
    (legit_dir / "index.html").write_text(LEGIT_PAGE, encoding="utf-8")
    (evil_dir / "index.html").write_text(EVIL_PAGE, encoding="utf-8")
    router_srv = tmpdir / "router_server.py"
    router_srv.write_text(ROUTER_HTTP_SCRIPT, encoding="utf-8")
    legit_log = tmpdir / "legit_http.log"
    evil_log = tmpdir / "evil_http.log"
    legit_log.touch()
    evil_log.touch()

    procs = []
    try:
        # Alte Reste entfernen und 3 virtuelle Radios laden
        for ns in (NS_CLIENT, NS_EVIL, NS_LEGIT):
            run(["ip", "netns", "del", ns], check=False, capture=True)
        shutil.rmtree(CTRL_DIR, ignore_errors=True)
        run(["modprobe", "-r", "mac80211_hwsim"], check=False, capture=True)
        run(["modprobe", "mac80211_hwsim", "radios=3"])
        time.sleep(0.5)

        phys = hwsim_phys()
        if len(phys) < 3:
            sys.exit(f"Erwartet 3 mac80211_hwsim Radios, gefunden: {phys}")

        for ns, phy in zip((NS_LEGIT, NS_EVIL, NS_CLIENT), phys[:3]):
            run(["ip", "netns", "add", ns])
            ns_cmd(ns, "ip", "link", "set", "lo", "up")
            run(["iw", "phy", phy, "set", "netns", "name", ns])

        if_legit = iface_in_ns(NS_LEGIT)
        if_evil = iface_in_ns(NS_EVIL)
        if_client = iface_in_ns(NS_CLIENT)

        for ns, iface, mac in (
            (NS_LEGIT, if_legit, BSSID_REAL),
            (NS_EVIL, if_evil, BSSID_EVIL),
            (NS_CLIENT, if_client, MAC_CLIENT),
        ):
            ns_cmd(ns, "ip", "link", "set", iface, "down")
            ns_cmd(ns, "ip", "link", "set", iface, "address", mac)
            ns_cmd(ns, "ip", "link", "set", iface, "up")

        conf_legit = tmpdir / "hostapd_legit.conf"
        conf_evil = tmpdir / "hostapd_evil.conf"
        conf_wpa = tmpdir / "wpa_client.conf"
        write_hostapd_conf(conf_legit, if_legit, BSSID_REAL, 6, args.mode)
        write_hostapd_conf(conf_evil, if_evil, BSSID_EVIL, 11, args.mode)
        write_wpa_conf(conf_wpa, args.mode)

        print(f"[*] Starte legitimen Campus-AP ({SSID}, BSSID {BSSID_REAL}, Modus: {args.mode})...")
        procs.append(
            subprocess.Popen(
                ["ip", "netns", "exec", NS_LEGIT, "hostapd", str(conf_legit)],
                stdout=open(tmpdir / "legit_ap.log", "w"),
                stderr=subprocess.STDOUT,
            )
        )
        time.sleep(1.5)
        ns_cmd(NS_LEGIT, "ip", "addr", "replace", "10.0.0.1/24", "dev", if_legit)
        procs.append(
            subprocess.Popen(
                ["ip", "netns", "exec", NS_LEGIT, "python3", str(router_srv), "ROUTER-1 :11", str(legit_dir), str(legit_log)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        )

        print(f"[*] Verbinde virtuellen Client ({MAC_CLIENT}) mit {SSID}...")
        ns_cmd(NS_CLIENT, "ip", "addr", "replace", "10.0.0.10/24", "dev", if_client)
        procs.append(
            subprocess.Popen(
                ["ip", "netns", "exec", NS_CLIENT, "wpa_supplicant", "-D", "nl80211", "-i", if_client, "-c", str(conf_wpa)],
                stdout=open(tmpdir / "client.log", "w"),
                stderr=subprocess.STDOUT,
            )
        )
        wait_connected(if_client)

        evil_started = False

        def start_evil():
            nonlocal evil_started
            if evil_started:
                return
            print(f"\n[*] Starte Evil-Twin-AP ({SSID}, BSSID {BSSID_EVIL})...")
            procs.append(
                subprocess.Popen(
                    ["ip", "netns", "exec", NS_EVIL, "hostapd", str(conf_evil)],
                    stdout=open(tmpdir / "evil_ap.log", "w"),
                    stderr=subprocess.STDOUT,
                )
            )
            time.sleep(1.5)
            ns_cmd(NS_EVIL, "ip", "addr", "replace", "10.0.0.1/24", "dev", if_evil)
            procs.append(
                subprocess.Popen(
                    ["ip", "netns", "exec", NS_EVIL, "python3", str(router_srv), "ROUTER-2 :22", str(evil_dir), str(evil_log)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            )
            evil_started = True
            print("[*] Evil Twin läuft.")

        print("\n=== Virtuelle Evil-Twin-Demo bereit (kein reales Funksignal) ===")
        show_status(if_client)

        while True:
            print(
                "\n--- Demo-Menü ---\n"
                "  [1] Status & Zielseite anzeigen (iw link + curl)\n"
                "  [2] WLAN-Scan anzeigen (alle sichtbaren APs)\n"
                "  [3] Evil Twin (:22) starten\n"
                "  [4] Client auf Evil Twin (:22) wechseln & Portal zeigen\n"
                "  [5] Zurück zum legitimen Campus-AP (:11)\n"
                "  [6] Portal im Browser des virtuellen Clients öffnen\n"
                "  [7] 8 Sekunden virtuelle 802.11-Pakete anzeigen\n"
                "  [8] Router-Sicht anzeigen (Clients + HTTP-Logs von Router 1 & 2)\n"
                "  [9] Live-Monitor (Router-Traffic in Echtzeit mitlesen)\n"
                "  [q] Beenden & aufräumen"
            )
            try:
                choice = input("Auswahl > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break
            if choice == "1":
                show_status(if_client)
            elif choice == "2":
                show_scan(if_client)
            elif choice == "3":
                start_evil()
            elif choice == "4":
                start_evil()
                roam_client(if_client, BSSID_EVIL)
            elif choice == "5":
                roam_client(if_client, BSSID_REAL)
            elif choice == "6":
                open_portal()
            elif choice == "7":
                show_packet_trace()
            elif choice == "8":
                show_router_view(if_legit, if_evil, legit_log, evil_log, evil_started)
            elif choice == "9":
                live_router_monitor(legit_log, evil_log)
            elif choice == "q":
                break
    finally:
        cleanup(procs, tmpdir)


if __name__ == "__main__":
    main()
