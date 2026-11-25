VIRTUELLE EVIL-TWIN-DEMO (Kali / Linux mit mac80211_hwsim)

Diese Demo erzeugt 3 virtuelle Wi-Fi-Radios direkt im Linux-Kernel
(ohne Mininet-WiFi und ohne USB-WLAN-Adapter).
Es werden keine realen Funkframes nach außen gesendet.

Einmalig installieren (Kali/Ubuntu/Debian):
  sudo apt update && sudo apt install -y hostapd wpasupplicant iw iproute2 curl tshark firefox-esr

Start (Standard WPA2, optional --mode wpa3 oder --mode open):
  sudo python3 lab/evil_twin_lab.py

Mit Kali-WLAN-Einstellungen oben rechts (--kali-ui, benötigt dnsmasq-base):
  sudo apt install -y dnsmasq-base
  sudo -E python3 lab/evil_twin_lab.py --kali-ui

Ablauf im interaktiven Menü:
  [1] Status & Zielseite zeigen (verbunden mit Campus-AP :11)
  [3] Evil Twin (:22) mit derselben SSID 'Seminar-Gast' starten
  [2] WLAN-Scan zeigen (beide 'Seminar-Gast' APs sichtbar)
  [4] Client auf Evil Twin (:22) wechseln -> dieselbe URL zeigt Fake-Portal
  [6] Browser im virtuellen Client-Netzwerk mit grafischem Portal öffnen
  [7] 8 Sekunden echte virtuelle 802.11-Pakete über tshark anzeigen
  [8] Router-Sicht: Verbundene Clients & HTTP-Logs beider Router (:11 vs. :22)
  [9] Live-Monitor: Traffic auf Router 1 & Router 2 in Echtzeit mitlesen
  [10] Router 1 trennt deinen Client (hostapd 'Gerät trennen', wie Router-Admin-UI)
  [11] Router 2 trennt deinen Client (hostapd 'Gerät trennen', wie Router-Admin-UI)

Sicherheitsgrenzen der Demo:
  - Kein gespoofter Deauth-Angriff: [10]/[11] nutzen hostapd_cli deauthenticate,
    d.h. der jeweils EIGENE AP trennt seinen EIGENEN, bereits verbundenen
    Client über sein eigenes Kontrollinterface (ctrl_interface). Das ist
    technisch dasselbe wie der "Gerät trennen"-Knopf im Router-Admin-UI und
    KEIN gefälschter Deauth-Frame mit fremder Absender-BSSID.
  - Keine DNS-Manipulation: Die Seite ist nur direkt über 10.0.0.1:8080 erreichbar.
  - Keine Datenerfassung: Das Fake-Portal nutzt nur schreibgeschützte Dummy-
    Werte. Der Demo-Button erzeugt ausschließlich GET /demo-freigegeben.

Optional PCAP (zweites Terminal):
  sudo ip link set hwsim0 up
  sudo tshark -i hwsim0 -w lab_demo.pcapng

Browser manuell öffnen (falls die Menüoption wegen Wayland/Display-Setup
nicht funktioniert):
  sudo ip netns exec et_client firefox-esr http://10.0.0.1:8080

Siehe VIRTUELLE_DEMO_ANLEITUNG.md.
