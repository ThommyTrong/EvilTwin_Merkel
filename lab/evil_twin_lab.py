#!/usr/bin/env python3

"""
Virtual-only Evil-Twin teaching demo.

This script requires Mininet-WiFi and mac80211_hwsim. It intentionally uses
the laboratory SSID EVILTWIN-LAB-47 and does not configure a real host WLAN.
"""

import os
import sys
import time

try:
    from mn_wifi.net import Mininet_wifi
except ImportError:
    sys.exit(
        "Mininet-WiFi ist nicht installiert. Siehe VIRTUELLE_DEMO_ANLEITUNG.md."
    )


SSID = "EVILTWIN-LAB-47"


def add_station(net):
    return net.addStation(
        "sta1",
        position="20,20,0",
    )


def add_real_lab_ap(net):
    return net.addAccessPoint(
        "ap1",
        ssid=SSID,
        mode="g",
        channel="6",
        ieee80211w="0",
        position="30,20,0",
    )


def add_evil_lab_ap(net):
    return net.addAccessPoint(
        "ap2",
        ssid=SSID,
        mode="g",
        channel="11",
        ieee80211w="0",
        position="10,20,0",
    )


def print_status(net, station):
    print("\n--- Virtuelle Laborumgebung ---")
    print(f"SSID: {SSID}")
    print("Nur hwsim/Mininet-WiFi-Schnittstellen; kein reales Funkgerät.")
    print("\nStation status:")
    print(station.cmd("iw dev sta1-wlan0 link"))
    print("\nStation scan:")
    print(station.cmd("iw dev sta1-wlan0 scan | grep -E 'BSS|SSID|signal'"))


def main():
    if os.geteuid() != 0:
        sys.exit("Bitte mit sudo ausführen: sudo python3 lab/evil_twin_lab.py")

    net = Mininet_wifi()
    station = add_station(net)
    ap_real = add_real_lab_ap(net)
    ap_evil = add_evil_lab_ap(net)

    net.configureWifiNodes()
    net.build()

    print("\nStarte legale Labor-APs...")
    ap_real.start([])
    ap_evil.start([])

    station.setRange(70)
    time.sleep(2)

    print_status(net, station)

    print("\nWPA2-Demo:")
    print("  1. Verbindung der Station zum echten AP beobachten")
    print("  2. station disconnect")
    print("  3. station reassociate")
    print("  4. iw dev sta1-wlan0 link")
    print("  5. Terminalstatus mit scan vergleichen")

    print("\nMininet-CLI:")
    print("  sta1 iw dev sta1-wlan0 link")
    print("  sta1 iw dev sta1-wlan0 scan")
    print("  sta1 iw dev sta1-wlan0 disconnect")
    print("  sta1 wpa_cli -i sta1-wlan0 reassociate")
    print("  sta1 iw dev sta1-wlan0 link")

    net.start()
    net.interact()
    net.stop()


if __name__ == "__main__":
    main()
