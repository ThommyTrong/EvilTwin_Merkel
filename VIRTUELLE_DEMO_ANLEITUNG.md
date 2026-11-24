# Virtuelle Evil-Twin-Demo mit Mininet-WiFi

Diese Anleitung startet einen **vollständig virtuellen 802.11-Versuch**. Es werden
keine realen WLAN-Funkframes gesendet. Dafür werden virtuelle Radios mit
`mac80211_hwsim`, virtuelle Access Points mit `hostapd` und eine virtuelle
Station mit `wpa_supplicant` erstellt.

## Zweck

Die Demo zeigt:

1. Zwei Access Points mit derselben SSID
2. Unterschiedliche BSSIDs
3. Verbindungs- und Disconnect-Zustände
4. Wahl des stärkeren bzw. bevorzugten virtuellen AP
5. WPA2-PSK und WPA3-SAE als Varianten
6. Reale Linux-WLAN-Statusbefehle und optional einen PCAP-Ausschnitt

Die Variante ersetzt keinen externen Funk-Adapter. Sie ist für eine
PowerPoint-Live-Demo auf einem Seminar-PC gedacht.

## Voraussetzungen

Empfohlen:

- Ubuntu 22.04 oder 24.04 als native VM oder direkt auf einem Linux-PC
- mindestens 4 GB RAM
- VirtualBox oder VMware
- virtuelle Hardware ohne USB-WLAN-Weiterleitung
- Internetzugang nur für die Installation
- 10 GB freien Speicherplatz

VMware oder VirtualBox sollten eine Linux-VM mit NAT verwenden. Die virtuelle
WLAN-Umgebung benötigt keine reale WLAN-Schnittstelle und keine USB-Passthrough-
Konfiguration.

## 1. Ubuntu-VM vorbereiten

In der Ubuntu-VM:

```bash
sudo apt update
sudo apt install -y git wget curl python3 python3-pip \
  openvswitch-switch hostapd wpa-supplicant iw wireless-tools \
  net-tools tcpdump wireshark tshark
```

Bei der Wireshark-Frage „DUMPCap als nicht-root ausführen?“ mit **Ja**
antworten, falls Wireshark benutzt werden soll.

Optional Mininet-WiFi:

```bash
git clone https://github.com/intrig-unicamp/mininet-wifi.git
cd mininet-wifi
sudo ./install.sh -W
```

Die Installation der Mininet-WiFi-Abhängigkeiten kann mehrere Minuten dauern.
Nach der Installation VM neu starten und testen:

```bash
sudo modprobe mac80211_hwsim
iw dev
```

Vor dem Neustart der VM sollte keine laufende virtuelle WLAN-Demo existieren.

## 2. Dateien aus diesem Repository benutzen

Das Demo-Script liegt in:

```text
lab/evil_twin_lab.py
```

Es startet:

- einen legitimen virtuellen AP
- einen Evil-Twin-AP
- eine virtuelle WLAN-Station
- virtuelle Access-Point-Interfaces

Die SSID ist absichtlich eine Laborkennung:

```text
EVILTWIN-LAB-47
```

## 3. Demo starten

Ein Terminal in der VM öffnen:

```bash
cd /pfad/zum/Repository
sudo python3 lab/evil_twin_lab.py
```

Die virtuellen Komponenten werden erzeugt. Die Befehle `iw` und
`wpa_cli` werden in der Mininet-CLI ausgeführt.

## 4. Demo-Befehle in der Mininet-CLI

Den vollen Status anzeigen:

```text
mn> sta1 iw dev sta1-wlan0 link
mn> sta1 iw dev sta1-wlan0 scan
mn> sta1 wpa_cli -i sta1-wlan0 status
```

Die virtuellen APs anzeigen:

```text
mn> ap1 iw dev ap1-wlan1 info
mn> ap2 iw dev ap2-wlan1 info
```

Nur die Demo-Trennung ausführen:

```text
mn> sta1 iw dev sta1-wlan0 disconnect
mn> sta1 wpa_cli -i sta1-wlan0 reassociate
mn> sta1 iw dev sta1-wlan0 link
```

Diese Befehle sind interne Linux-WLAN-Befehle innerhalb der VM. Sie senden keine
WLAN-Pakete an reale Geräte in der Umgebung.

Für die Ansicht in Wireshark:

```bash
sudo tshark -I -i wlan0 -f "type mgt" -T fields \
  -e frame.time_relative \
  -e wlan.da \
  -e wlan.sa \
  -e wlan.ssid \
  -e wlan.fc.type_subtype
```

Das Interface `wlan0` kann je nach VM `hwsim0`, `hwsim1` oder einen anderen Namen
haben. Ermitteln:

```bash
iw dev
ip -brief link
```

## 5. Vergleich WPA2 gegen WPA3

Für den Vortrag kann die erste Runde **WPA2-PSK** verwenden. In der zweiten Runde
werden dieselben Befehle mit `WPA3-SAE` und PMF ausgeführt.

Wichtig: WPA3- und PMF-Unterstützung hängt von der hostapd-/wpa_supplicant-
Version ab. Vor dem Vortrag testen:

```bash
hostapd -v
wpa_supplicant -v
```

Ein separates WPA3-Setup wird erst gestartet, wenn WPA2 erfolgreich läuft.

## 6. PCAP erstellen

```bash
sudo tshark -I -i hwsim0 -w lab_demo.pcapng
```

Beendet wird die Aufnahme mit `Strg+C`. Danach in Wireshark öffnen:

```text
wlan.ssid contains "EVILTWIN-LAB"
```

Für Präsentationsfolien filtert man:

```text
wlan.fc.type_subtype == 0x0008
wlan.fc.type_subtype == 0x000c
wlan.fc.type_subtype == 0x0000
wlan.fc.type_subtype == 0x0001
```

## 7. Vorherige Aufnahme als Fallback

Vor dem Vortrag mindestens einmal eine PCAP-Datei erzeugen und speichern:

```text
lab_evil_twin_wpa2.pcapng
lab_evil_twin_wpa3.pcapng
```

Im Zweifel nur PCAP in Wireshark anzeigen. Die Live-Simulation muss nicht
gestartet werden.

## 8. Senden nach außen verhindern

Diese Demo verwendet kein USB-WLAN-Gerät. In VirtualBox oder VMware:

- USB-WLAN-Passthrough deaktiviert lassen
- WLAN-Karte nicht in die VM durchreichen
- keine echte SSID verwenden
- keine echte MAC-Adresse verwenden
- keine fremden Geräte erreichen

Die virtuelle Laborumgebung bleibt auf Linux-Namespaces und virtualisierte Radios
beschränkt.

## Quellen

- Mininet-WiFi: https://mininet-wifi.github.io/
- GitHub: https://github.com/intrig-unicamp/mininet-wifi
- Wireshark: https://www.wireshark.org/
- hostapd/wpa_supplicant: https://w1.fi/
- Linux mac80211_hwsim: https://wireless.docs.kernel.org/
