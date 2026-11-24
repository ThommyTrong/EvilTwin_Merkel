# Evil Twin - Präsentations-Notizen
## 20-Minütige DHBW Praxisarbeit Verteidigung

---

## 🎯 ZEITPLAN (20 Minuten)

| Zeit | Folie | Thema | Sprechzeit |
|------|-------|-------|-----------|
| 0:00-1:30 | 1 | Willkommen & Titel | 1:30 |
| 1:30-3:00 | 2 | Einleitung (Warum Evil Twin?) | 1:30 |
| 3:00-4:30 | 3 | Definition & Grundkonzept | 1:30 |
| 4:30-6:30 | 4 | Angriffsvektoren (Passive/Active) | 2:00 |
| 6:30-8:30 | 5 | Technische Implementierung | 2:00 |
| 8:30-11:00 | 6 | 🔴 **LIVE DEMO** (Wireshark!) | 2:30 |
| 11:00-13:00 | 7 | Schutzmassnahmen & Defense | 2:00 |
| 13:00-14:30 | 8 | Legale & Ethische Aspekte | 1:30 |
| 14:30-16:00 | 9 | Quellen & Fragen | 1:30 |

**TOTAL: ~16 Minuten Präsentation + ~4 Minuten Fragen = 20 Minuten**

---

## 📋 SPRECHNOTIZEN PRO FOLIE

### Folie 1: TITELFOLIE
```
"Guten Tag! Wir präsentieren unsere Praxisarbeit zum Thema 'Evil Twin' 
im Kontext von Offensive Security. Evil Twin ist eine der gefährlichsten 
und am häufigsten vorkommenden WLAN-Attacken in der Praxis. 

Innerhalb der nächsten 20 Minuten werden wir euch zeigen:
- Was Evil Twin ist und wie die Attacke funktioniert
- Wie Hacker diese Technik praktizieren
- Echte LIVE-Demonstration mit Wireshark
- Wie man sich davor schützt
- Rechtliche Implikationen"
```

### Folie 2: EINLEITUNG
```
"Evil Twin ist nicht nur theoretisch interessant - es passiert täglich:

1. An Flughäfen - Geschäftsleute verbinden sich mit 'AirportFree'
2. In Cafés - Starbucks-WLAN ist perfekter Evil Twin Kandidat
3. Hotels - Gäste vertrauen automatisch dem Hotel-WLAN
4. Konferenzen - Insider-Spionage auf Konferenzen

Die Attacke ist so wirkungsvoll, weil:
- Clients WOLLEN sich damit verbinden
- Sie sieht aus wie legitim
- Sie benötigt keine Passwort-Brute-Force
- Unverschlüsselte Daten sind sofort sichtbar"
```

### Folie 3: DEFINITION
```
"Ein Evil Twin ist ein rogue access point - ein unautorisierten Netzwerk-Zugangspunkt.

Er ahmt einen legitimen WiFi-Namen nach (SSID).
Der Unterschied zu echtem WiFi-Hacking ist wichtig:
- WiFi Cracking: Brute-Force des Passworts
- WiFi Jamming: Netzwerk blockieren (einfach, aber auch einfach zu sehen)
- Evil Twin: Clients WÄHLEN freiwillig die 'falsche' Variante

Das Resultat: Der Angreifer sitzt als MITM (Man-in-the-Middle) 
und sieht ALLES zwischen Client und echtem Internet."
```

### Folie 4: ANGRIFFSVEKTOREN
```
"Es gibt zwei Arten von Angriffsszenarien:

PASSIVE ATTACKS (schwer zu detektieren):
- Packet Sniffing: Wir lesen einfach alle unverschlüsselten Pakete mit
  → Login-Daten, E-Mails, Chats, Passwörter
- Session Hijacking: Browser-Cookies stehlen
  → Ohne Logout in Konten eindringen (Facebook, Gmail, etc.)
- Credential Harvesting: Alle Login-Versuche sammeln

AKTIVE ATTACKS (manipulativ):
- DNS Spoofing: Angreifer beantwortet DNS-Anfragen falsch
  → 'google.com' zeigt auf Angreifer-Server
  → Fake-Phishing-Seite für Banking/Credentials
- SSL Stripping: HTTPS zu HTTP herunterstufeln
  → Zertifikats-Validierung bypass
- ARP Spoofing: Netzwerk-Paket-Umleitung
- Malware-Injection: Dateien beim Download infizieren"
```

### Folie 5: IMPLEMENTIERUNG
```
"Technisch ist Evil Twin SEHR einfach zu bauen!

HARDWARE:
- Ein Linux-Computer (oder Raspberry Pi)
- Ein WLAN-Adapter, der im Monitor-Modus läuft
- Optional: 2. WLAN für echten Internet-Zugang

SOFTWARE:
- hostapd: Erstellt den Access Point
- aircrack-ng: Scannt und analysiert Netzwerke
- dnsmasq: Vergibt IP-Adressen an Clients (DHCP)
- ettercap oder mitmproxy: Führt MITM-Angriffe durch
- Wireshark: Zeigt den Datenverkehr

Die ganze Attacke lädt in <5 Minuten auf!"
```

### Folie 6: LIVE DEMO ⭐
```
"Jetzt kommt der praktische Teil! Wir zeigen euch ein Angriffsszenario 
in unserem isolierten Labor.

[LIVE DEMO starten - Blender oder virtuelle Umgebung]

SCHRITT 1: Evil Twin starten
- 'sudo hostapd -c evil_twin.conf'
- Access Point 'AirportFree' ist jetzt sichtbar

SCHRITT 2: Test-Client verbindung
- Simulierter Client verbindet sich
- IP-Adresse wird via DHCP vergeben

SCHRITT 3: WIRESHARK ÖFFNEN
- Live-Capture starten
- Hier können wir jede einzelne Paket sehen!

SCHRITT 4: Daten abfangen
- Client öffnet http://banking.example.com
- Username/Passwort gehen unverschlüsselt über den Draht!
- Wir sehen es ALLE in Wireshark!

SCHRITT 5: Mit HTTPS vergleichen
- Wenn HTTPS verwendet wird: Verschlüsseltes Payload
- Trotzdem sehen wir die Domain (SNI Leakage)

🔑 KEY INSIGHT: HTTP ist nicht zu verwenden! Immer HTTPS!"
```

### Folie 7: SCHUTZMASSNAHMEN
```
"Wie können wir uns schützen? Es gibt viele Optionen:

FÜR ENDBENUTZER:
- VPN verwenden (z.B. ProtonVPN, Surfshark)
  → Verschlüsselt ALLES zwischen dir und VPN-Server
  → Evil Twin sieht nur verschlüsselte Daten
- HTTPS überall (Browser-Warnung beachten!)
- Zertifikate kritisch überprüfen
- Für sensible Daten: Öffentliches WLAN vermeiden

FÜR ADMINISTRATOREN:
- 802.1X Authentifizierung
  → Nur registrierte Clients können verbinden
- Regelmäßige WLAN-Scans (Rogue AP Detection)
- WPA3 statt WPA2 (neuerer Standard)
- Anomalie-Erkennung
  → Abnormale Muster erkennen

DAS BESTE: Kombination aus mehreren Massnahmen!"
```

### Folie 8: LEGALE ASPEKTE
```
"Hier muss ich SEHR KLAR sein:

⛔ Evil Twin Attacken sind STRAFBAR:
- Bundesrepublik Deutschland: StGB § 263a (Betrug)
                              StGB § 269 (Datenfälschung)
                              StGB § 303a (Datenveränderung)
- Österreich: Ähnliche Paragraphen
- Schweiz: StGB Artikel 143 (Unbefugter Zugriff)

STRAFE: Bis zu 10 Jahre Freiheitsstrafe oder Geldstrafen

✅ LEGAL ist:
- Penetration Testing mit schriftlicher Genehmigung
- Forschung & Bildung in ISOLIERTEN Laboren
- Schwachstellen-Meldung (Responsible Disclosure)
- Bug Bounty Programme

🎓 UNSERE POSITION:
- Diese Präsentation ist rein BILDUNGSZWECK
- Lab-Demo mit statischen Clients (keine echten Personen)
- Ziel: Verständnis für bessere Sicherheit
- Wir verbreiten DEFENSIVE Knowledge"
```

### Folie 9: QUELLEN & FRAGEN
```
"Hier sind unsere Quellen für diese Präsentation.
Wenn ihr mehr erfahren wollt, schaut auf:
- OWASP.org (kostenlos, sehr gut)
- Kali Linux Dokumentation
- IEEE 802.11 Standards
- NIST Cybersecurity Framework

Fragen?"
```

---

## 🎬 DEMO-SKRIPT DETAILLIERT

### Demo Setup
```bash
# Terminal 1: Evil Twin starten
sudo hostapd -c /etc/hostapd/hostapd.conf

# Terminal 2: DHCP Server (dnsmasq)
sudo dnsmasq -C /etc/dnsmasq.conf

# Terminal 3: Wireshark FILTER für bessere Sicht
# Filter: http || dns || tcp.port==80
# Oder einfach: tcp.port==80 or tcp.port==443
```

### Was wird gezeigt:
1. ✅ Netzwerk-Liste zeigt "AirportFree" (Evil Twin)
2. ✅ Client verbindet sich
3. ✅ Wireshark zeigt HTTP Passwörter im Klartext
4. ✅ HTTPS Traffic sieht verschlüsselt aus
5. ✅ DNS Spoofing Demo (optional)

### Troubleshooting bei Live Demo
- Wenn Wireshark keine Pakete zeigt: Interface auf richtig setzen
- Wenn Client nicht verbindet: IP-Subnet überprüfen
- Wenn DNS Spoofing nicht geht: dnsmasq Konfiguration checken

---

## 📊 KEY TALKING POINTS

✅ **Evil Twin ist REAL und HÄUFIG**
- Täglich tausende Attacken weltweit
- Einfach zu bauen
- Schwer zu detektieren

✅ **Die Attacke funktioniert, weil Menschen VERTRAUEN**
- "AirportFree" = "muss legitim sein"
- Keine technischen Barrieren
- Social Engineering + Technik

✅ **Daten ohne Verschlüsselung = VERLOREN**
- HTTP ist nicht sicher
- VPN ist der beste Schutz
- HTTPS hilft auch

✅ **Legale Konsequenzen sind ERNST**
- Nicht einfach "experimentieren"
- Genehmigung ist notwendig
- Verantwortung ist wichtig

---

## ❓ POTENZIELLE FRAGEN

**F: "Kann man Evil Twin auf Android/iPhone machen?"**
A: "Ja, aber schwieriger. iOS/Android erlauben es nicht nativ. Man braucht Jailbreak/Root. Deshalb fokussieren sich Hacker auf Linux/Raspberry Pi."

**F: "Warum ist WPA3 besser?"**
A: "WPA3 hat Individualized Data Encryption (OWE). Jeder Client hat eigene Verschlüsselung - selbst wenn die SSID geklont ist, sind Passwörter sicher."

**F: "Kann VPN einen Evil Twin schlagen?"**
A: "100%. VPN verschlüsselt ALLES zwischen dir und dem VPN-Server. Evil Twin sieht nur verschlüsselte Daten. VPN ist die beste Verteidigung."

**F: "Wie detektiert man Evil Twins?"**
A: "Tools wie Kismet können mehrere APs mit gleicher SSID erkennen. Signal-Stärke-Analyse hilft auch. Aber für Endbenutzer schwierig."

---

## 🎨 DESIGN-NOTIZEN

- Alle Folien haben einheitliches DHBW-Branding (Rot)
- Rechte Sidebar zeigt aktuelle Position in der Agenda
- Klare Bullet Points (nicht zu viel Text)
- Live Demo hat eigene Folie für Fokus
- Quellen-Folie ist professionell und vollständig

---

## ✨ TIPPS FÜR ERFOLGREICHE PRÄSENTATION

1. **Pacing**: Nicht zu schnell reden. 20 Min = ausreichend Zeit.
2. **Eye Contact**: Folien sind Hilfsmittel, nicht der Star.
3. **Live Demo**: 2-3 Minuten max. - danach "back to slides"
4. **Praxis-Beispiele**: "An eurem Flughafen passiert das täglich!"
5. **Interaktion**: Am Ende Fragen einplanen, nicht gehetzt sein
6. **Körpersprache**: Sicher, professionell, enthusiastisch
7. **Backup**: Screenshots von Demo im PDF mitnehmen (falls Demo crashed)

---

## 📱 EQUIPMENT-CHECKLISTE

- [ ] Laptop mit Präsentation
- [ ] Beamer/HDMI-Kabel
- [ ] Demo-Setup (Kali Linux mit aircrack-ng)
- [ ] Wireshark instaliert & getestet
- [ ] Backup-Präsentation auf USB-Stick
- [ ] Sprechzettel ausgedruckt
- [ ] Wasser für die Kehle

---

## 🚀 VIEL ERFOLG!

Viel Erfolg bei der Präsentation! 
Evil Twin ist ein spannendes Thema und eure DHBW wird das Fachwissen schätzen.

**Faustregel**: Ruhe bewahren, Fachwissen zeigen, Demo live demonstrieren!

---

*Erstellt mit python-pptx*
*Version: 1.0 | DHBW Format*
