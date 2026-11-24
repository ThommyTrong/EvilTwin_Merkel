# Virtuelle Evil-Twin-Demo auf Kali/Linux (mac80211_hwsim)

Diese Anleitung startet einen **vollständig virtuellen 802.11-Versuch** direkt
unter Kali Linux (auch `aarch64` / Apple Silicon) — **ohne Mininet-WiFi und
ohne USB-WLAN-Adapter**. Es werden keine realen WLAN-Funkframes gesendet.
Dafür nutzt das Skript das Linux-Kernel-Modul `mac80211_hwsim`, Linux Network
Namespaces (`ip netns`), `hostapd` und `wpa_supplicant`.

## Zweck

Die Demo zeigt:

1. Zwei Access Points mit derselben SSID (`Seminar-Gast`)
2. Unterschiedliche BSSIDs (`02:00:00:00:00:11` vs. `02:00:00:00:00:22`)
3. Sichtbare Auswirkung für den Nutzer: Dieselbe URL (`http://10.0.0.1:8080`)
   liefert beim echten AP das Campus-Portal und beim Evil Twin das simulierte
   Fake-Portal (ohne Datenerfassung)
4. Vergleich zwischen `--mode open`, `--mode wpa2` und `--mode wpa3`
5. Optional echte 802.11-Management-Frames in Wireshark über `hwsim0`

## 1. Kali-VM vorbereiten (einmalig)

In der Kali-VM:

```bash
sudo apt update
sudo apt install -y git curl python3 hostapd wpasupplicant iw iproute2 tshark wireshark
```

Kurz prüfen, ob `mac80211_hwsim` im Kernel vorhanden ist:

```bash
sudo modprobe mac80211_hwsim radios=3 && iw dev
```

*(Dort sollten `wlan0`, `wlan1` und `wlan2` erscheinen.)*

## 2. Repository holen

```bash
git clone https://github.com/ThommyTrong/EvilTwin_Merkel.git
cd EvilTwin_Merkel
```

## 3. Demo starten

```bash
sudo python3 lab/evil_twin_lab.py               # Standard: WPA2 (PMF aus)
sudo python3 lab/evil_twin_lab.py --mode wpa3   # Vergleich: WPA3 + PMF
sudo python3 lab/evil_twin_lab.py --mode open   # Offenes Gast-WLAN
```

## 4. Ablauf im interaktiven Demo-Menü

1. **[1] Status & Zielseite:** Client ist mit `02:00:00:00:00:11` verbunden, `http://10.0.0.1:8080` zeigt das legitime Campus-Portal.
2. **[3] Evil Twin starten:** Zweiter AP (`02:00:00:00:00:22`) startet mit identischer SSID `Seminar-Gast`.
3. **[2] WLAN-Scan:** Zeigt beide gleichnamigen Access Points im Scan.
4. **[4] Wechsel auf Evil Twin:** Client wechselt auf `:22`; dieselbe URL `http://10.0.0.1:8080` liefert jetzt das simulierte Evil-Twin-Portal.
5. **[q] Beenden:** Stoppt alle Prozesse, löscht die Namespaces und entlädt `mac80211_hwsim`.

## 5. Optional: Wireshark / PCAP mitlaufen lassen

In einem zweiten Terminal (während die Demo läuft):

```bash
sudo ip link set hwsim0 up
sudo tshark -i hwsim0 -w lab_demo.pcapng
```

Danach in Wireshark öffnen mit Filter:

```text
wlan.ssid == "Seminar-Gast"
```

## 6. Senden nach außen verhindern

Diese Demo verwendet kein USB-WLAN-Gerät und keine reale WLAN-Schnittstelle.
Alle drei virtuellen Radios existieren ausschließlich im Kernel (`mac80211_hwsim`)
und in isolierten Namespaces (`et_legit`, `et_evil`, `et_client`).
