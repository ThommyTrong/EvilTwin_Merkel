VIRTUELLE EVIL-TWIN-DEMO

Diese Demo erzeugt virtuelle Wi-Fi-Schnittstellen in einer Linux-VM.
Es werden keine echten Funk- oder Paketinjections-Funktionen aktiviert.

Start:
  sudo python3 lab/evil_twin_lab.py

CLI:
  sta1 iw dev sta1-wlan0 link
  sta1 iw dev sta1-wlan0 scan
  sta1 iw dev sta1-wlan0 disconnect
  sta1 wpa_cli -i sta1-wlan0 reassociate

PCAP:
  sudo tshark -I -i hwsim0 -w lab_demo.pcapng

Siehe VIRTUELLE_DEMO_ANLEITUNG.md.
