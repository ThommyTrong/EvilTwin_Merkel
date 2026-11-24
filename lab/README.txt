VIRTUELLE EVIL-TWIN-DEMO (Kali / Linux mit mac80211_hwsim)

Diese Demo erzeugt 3 virtuelle Wi-Fi-Radios direkt im Linux-Kernel
(ohne Mininet-WiFi und ohne USB-WLAN-Adapter).
Es werden keine realen Funkframes nach außen gesendet.

Einmalig installieren (Kali/Ubuntu/Debian):
  sudo apt update && sudo apt install -y hostapd wpasupplicant iw iproute2 curl tshark

Start (Standard WPA2, optional --mode wpa3 oder --mode open):
  sudo python3 lab/evil_twin_lab.py

Ablauf im interaktiven Menü:
  [1] Status & Zielseite zeigen (verbunden mit Campus-AP :11)
  [3] Evil Twin (:22) mit derselben SSID 'Seminar-Gast' starten
  [2] WLAN-Scan zeigen (beide 'Seminar-Gast' APs sichtbar)
  [4] Client auf Evil Twin (:22) wechseln -> dieselbe URL zeigt Fake-Portal

Optional PCAP (zweites Terminal):
  sudo ip link set hwsim0 up
  sudo tshark -i hwsim0 -w lab_demo.pcapng

Siehe VIRTUELLE_DEMO_ANLEITUNG.md.
