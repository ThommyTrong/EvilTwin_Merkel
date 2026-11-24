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

LEGIT_PAGE = """========================================
  CAMPUS-PORTAL (LEGITIMER AP :11)
========================================
Netz:   Seminar-Gast
BSSID:  02:00:00:00:00:11
Status: Verbunden mit Campus-Access-Point
Info:   Regulaerer Gastzugang ohne Konto-Login.
"""

EVIL_PAGE = """========================================
  [SIMULIERTES EVIL-TWIN-PORTAL :22]
========================================
Netz:   Seminar-Gast (identische SSID!)
BSSID:  02:00:00:00:00:22
Status: Verbunden mit ZWEITEM Access Point (Evil Twin)
Hinweis: Ein Angreifer koennte hier ein Fake-Login
         anzeigen. In dieser Demo wird nichts erfasst.
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
                ["ip", "netns", "exec", NS_LEGIT, "python3", "-m", "http.server", "8080", "--bind", "10.0.0.1", "--directory", str(legit_dir)],
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
                    ["ip", "netns", "exec", NS_EVIL, "python3", "-m", "http.server", "8080", "--bind", "10.0.0.1", "--directory", str(evil_dir)],
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
            elif choice == "q":
                break
    finally:
        cleanup(procs, tmpdir)


if __name__ == "__main__":
    main()
