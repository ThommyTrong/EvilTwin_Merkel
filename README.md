# 🎯 Evil Twin - DHBW Praxisarbeit Präsentation
## Komplettes Paket für 20-minütige Offensive Security Verteidigung

## 🖥️ Interaktive Web-Demo (empfohlen für die Präsentation)

Eine schön gestaltete, interaktive Browser-Visualisierung des kompletten
Evil-Twin-Ablaufs — Netzwerk-Topologie, Handy-Mockup, Frame-Log, alles live
konfigurierbar (SSID, Signalstärke, WPA2/WPA3, Deauth/Portal ein-/ausblendbar):

- [webdemo/index.html](webdemo/index.html) — einfach im Browser öffnen
- [webdemo/README.md](webdemo/README.md) — Bedienungsanleitung

Läuft komplett offline, ohne Installation, ohne echte Netzwerkdaten.

## Virtuelle Labor-Demo

Für die Live-Demo ohne echten WLAN-USB-Adapter siehe:

- [VIRTUELLE_DEMO_ANLEITUNG.md](VIRTUELLE_DEMO_ANLEITUNG.md)
- [lab/evil_twin_lab.py](lab/evil_twin_lab.py)
- [lab/README.txt](lab/README.txt)

Die Demo verwendet mac80211_hwsim und Mininet-WiFi. Es entstehen virtuelle
WLAN-Schnittstellen in einer Linux-VM; keine realen Funkframes verlassen die
VM.

---

## 📦 INHALT DIESES PAKETS

Du hast jetzt folgende Dateien erhalten:

### 🎨 HAUPTPRÄSENTATION
**📄 `Evil_Twin_Presentation.pptx`** (43 KB)
- ✅ 9 professionelle Folien
- ✅ DHBW Branding (Rot/Grau)
- ✅ Dynamische Navigations-Sidebar
- ✅ Live Demo Folie
- ✅ Vollständige Quellen
- ✅ Perfekt für Beamer/Projektor (16:9 Format)

### 📚 BEGLEIT-MATERIALIEN (Markdowns)

1. **📋 `PRAESENTATION_NOTIZEN.md`** (9.5 KB)
   - Komplette Sprechnotizen pro Folie
   - Detaillierter Zeitplan (20 Min)
   - Demo-Skript Step-by-Step
   - Häufig gestellte Fragen + Antworten
   - Tipps für erfolgreiche Präsentation
   
2. **🔧 `DEMO_REFERENZKARTE.md`** (7.1 KB)
   - Alle technischen Commands
   - Schritt-für-Schritt Demo-Ablauf
   - Wireshark-Filter und -Tipps
   - Troubleshooting-Guide
   - Was tun wenn Demo crashed?
   
3. **🎓 `GESAMTKOMPENDIUM.md`** (12 KB)
   - Komplette Vorbereitung (2 Wochen Plan)
   - Rollenverteilung mit Partner
   - Umfassende Checklisten
   - Pro-Tipps zur Beeindruckung
   - Häufige Betreuer-Fragen
   
4. **📊 `VERGLEICH_DIAGRAMME.md`** (14 KB)
   - Evil Twin vs. andere Attacken
   - Visueller Attack Flow
   - Defense Layers Diagramm
   - Detektionsmechanismen
   - Sicherheits-Checklisten
   - Real-World Statistiken

---

## 🚀 SCHNELLSTART (1 WOCHE VOR PRÄSENTATION)

### Tag 1: Präsentation Lesen
```
1. Öffne: Evil_Twin_Presentation.pptx
2. Gehe durch alle 9 Folien
3. Lese Sprechnotizen: PRAESENTATION_NOTIZEN.md
4. Markiere wichtige Punkte
5. Dauer: 30-45 Minuten
```

### Tag 2: Demo Vorbereiten
```
1. Lese: DEMO_REFERENZKARTE.md
2. Installiere Kali Linux (wenn noch nicht vorhanden)
3. Teste alle Kommandos einzeln
4. Führe komplette Demo 1x aus
5. Schreibe Screenshot mit jedem erfolgreichen Step
6. Dauer: 1-2 Stunden
```

### Tag 3: Mit Partner Absprechen
```
1. Lest zusammen: GESAMTKOMPENDIUM.md
2. Entscheidet wer welche Folie präsentiert
3. Testet Demo zusammen
4. Übt Übergaben zwischen den Folien
5. Dauer: 1 Stunde
```

### Tage 4-7: Üben & Optimieren
```
1. Präsentation MINDESTENS 5x komplett durchgehen
2. Demo MINDESTENS 5x üben
3. Timing checken (sollte 20 Min sein)
4. Mit Betreuer Fragen klären
5. Fallback-Strategie testen
```

---

## 📋 CHECKLISTE VOR PRÄSENTATION

### Hardware & Software
- [ ] Laptop ist geladener und funktioniert
- [ ] HDMI-Kabel/Adapter ist vorhanden
- [ ] Powerbank mitgenommen
- [ ] USB-Stick mit Präsentation mitgenommen
- [ ] Kali Linux ist installiert und getestet
- [ ] Alle Demo-Tools funktionieren
- [ ] Wireshark funktioniert mit wlan0
- [ ] Screenshots als PDF/Bilder vorhanden (Backup)

### Präsentation
- [ ] Evil_Twin_Presentation.pptx lädt ohne Fehler
- [ ] Alle Folien sind sichtbar
- [ ] DHBW Logo auf jeder Folie
- [ ] Navigation/Agenda funktioniert
- [ ] Live Demo Folie ist klar
- [ ] Quellen sind vollständig

### Sprechnotizen
- [ ] PRAESENTATION_NOTIZEN.md ausgedruckt
- [ ] Wichtige Punkte hervorgehoben
- [ ] Partner-Übergaben markiert
- [ ] Schwierige Begriffe phonetisch geschrieben
- [ ] Timing-Markierungen für 20 Minuten

### Persönlich
- [ ] 8+ Stunden Schlaf die Nacht davor
- [ ] Professionelle Kleidung parat
- [ ] Dusche vor Präsentation
- [ ] Toilette benutzt vor Präsentation
- [ ] Vertrauensselbstbewusstsein aufgebaut
- [ ] Wasser für die Kehle mitgenommen

---

## 🎬 DEMO-ZUSAMMENFASSUNG

### Was wird gezeigt?

Die Live Demo ist das Herzstück! Hier eine Übersicht:

```
SCHRITT 1: Evil Twin starten
  → hostapd -c evil.conf
  → Access Point "FreeAirport_Wifi" wird sichtbar

SCHRITT 2: Test-Client verbindung
  → Simulierter Client verbindet sich
  → Erhält IP via DHCP

SCHRITT 3: Wireshark öffnen & Traffic sniffing
  → Live-Capture starten
  → HTTP-Filter: "tcp.port==80"

SCHRITT 4: Daten abfangen
  → Client öffnet: http://banking.example.com
  → Client gibt Passwort ein
  → Wireshark zeigt: Passwort in KLARTEXT!

SCHRITT 5: Mit HTTPS vergleichen
  → Client öffnet: https://banking.example.com
  → Wireshark zeigt: VERSCHLÜSSELTER Payload
  → Lernpunkt: HTTPS schützt!

RESULTAT: 
  🚨 Demonstriert warum Evil Twin so gefährlich ist
  💡 Zeigt die Wichtigkeit von Verschlüsselung
  ✅ Praktischer Beweis des Konzepts
```

### Timing für Demo
- Länge: 2-3 Minuten
- Platzierung: Folie 6 (Mitte der Präsentation)
- Fallback: Screenshots + Erklärung

---

## 🎯 PRÜFUNGS-TIPPS

### Was die Betreuer bewerten

1. **Fachwissen** (40%)
   - Verstehen von Evil Twin Konzept
   - Technische Tiefe
   - Realistische Szenarien
   
2. **Präsentation** (30%)
   - Klare Struktur
   - Gute Sprechweise
   - Professionelles Design
   
3. **Praktische Demonstration** (30%)
   - Funktionierendes Demo
   - Live-Erkenntnis
   - Problemlösungs-Fähigkeiten

### Häufige Fragen & Antworten

Alle Antworten findest du in `PRAESENTATION_NOTIZEN.md`:
- "Warum ist Evil Twin effektiver als WiFi Cracking?"
- "Kann VPN Evil Twin verhindern?"
- "Ist dies legal?"
- "Wie schützen sich große Unternehmen?"
- etc.

---

## 📊 INHALT PRO FOLIE

| Folie | Thema | Zeit | Fokus |
|-------|-------|------|-------|
| 1 | TITELFOLIE | 1-2 Min | Willkommen, DHBW, Autor |
| 2 | EINLEITUNG | 1-2 Min | Warum Evil Twin relevant |
| 3 | DEFINITION | 1-2 Min | Was ist ein Evil Twin? |
| 4 | ANGRIFFSVEKTOREN | 2 Min | Passive + Aktive Attacks |
| 5 | IMPLEMENTIERUNG | 2 Min | Technische Tools |
| **6** | **LIVE DEMO** | **2-3 Min** | **⭐ Kernpunkt!** |
| 7 | SCHUTZMASSNAHMEN | 2 Min | Wie man sich schützt |
| 8 | LEGALE ASPEKTE | 1-2 Min | Rechtliche Implikationen |
| 9 | QUELLEN | 1-2 Min | Ressourcen, Fragen |
| | | **~20 Min** | **TOTAL** |

---

## 🎓 BONUS: WEITERFÜHRENDE RESSOURCEN

Nach der Präsentation könnten dich diese Themen interessieren:

```
OFFENSIVE SECURITY (nächster Level):
  → WiFi Cracking mit aircrack-ng
  → Metasploit Framework
  → Social Engineering Attacks
  → Physical Security Testing

DEFENSIVE SECURITY (Gegenseite):
  → 802.1X Implementierung
  → WLAN Intrusion Detection
  → Honeypots (Fake APs zum Fangen)
  → Network Monitoring Tools

ZERTIFIKATE & KARRIERE:
  → eJPT (eLearnSecurity Praktiker)
  → OSCP (Offensive Security Expert)
  → CEH (Certified Ethical Hacker)
  → GWAPT (GIAC Web Application Penetration Tester)

ONLINE QUELLEN:
  → HackTheBox.com (Praktische Labs)
  → TryHackMe.com (Interaktive Kurse)
  → PentesterAcademy.com (Tiefgreifende Kurse)
  → YouTube: John Hammond, LiveOverflow
```

---

## ⚡ PERFORMANCE-TIPPS

### Für bessere Präsentation

**SPRECHEN:**
- Nicht zu schnell reden (Nervosität!)
- Pausen machen zwischen Sätzen
- Atmen nicht vergessen!
- Eye Contact mit Betreuer

**BEWEGUNG:**
- Nicht zu viel herumlaufen
- Mit Gestiken arbeiten (nicht statisch stehen)
- Zu den Folien zeigen wenn relevant
- Professionelle Körpersprache

**TIMING:**
- Folie 1-5: Partner A (7-8 Min)
- Folie 6: Demo (2-3 Min)
- Folie 7-9: Partner B (5-6 Min)
- Fragen: 4-5 Min

**NOTFALL-SZENARIEN:**
- Demo crashed → Screenshots zeigen
- Betreuer unterbricht → Frage beantworten, weitermachen
- Zu schnell fertig → Vertiefungsbeispiele bereit
- Zu langsam → Übergänge schneller machen

---

## 📞 HILFE & SUPPORT

### Wenn etwas nicht funktioniert:

**Präsentation lässt sich nicht öffnen:**
- PowerPoint/LibreOffice/Google Slides verwenden
- Datei ist Unicode-kompatibel

**Demo funktioniert nicht:**
- Lese: DEMO_REFERENZKARTE.md → Troubleshooting
- Habe Screenshots als Fallback
- Erkläre mit Bildern

**Frage kann ich nicht beantworten:**
- Lese: PRAESENTATION_NOTIZEN.md → Häufige Fragen
- Oder: "Interessante Frage, darüber habe ich nicht recherchiert"
- Besser ehrlich als falsch antworten!

**Allgemeine Tipps:**
- Google die Fehlermeldung
- Stack Overflow für technische Fragen
- Kali Linux Forum für spezifische Tool-Probleme
- Reddit r/netsec für allgemeine Security Fragen

---

## ✨ DAS WICHTIGSTE

> "Die beste Präsentation ist nicht die mit den schönsten Folien,
>  sondern die, wo der Präsentant **WEISS WOVON ER SPRICHT**."

Dieses Paket hat dir alles gegeben was du brauchst. 

**Nächster Schritt: LERNEN UND ÜBEN!**

1. ✅ Verstehen (Präsentation lesen)
2. ✅ Praxis (Demo üben)
3. ✅ Präsentation (Übergaben mit Partner)
4. ✅ Vertrauen (Mehrfach üben bis sicher)
5. ✅ BÜHNE (Präsentation halten!)

---

## 🎉 VIEL ERFOLG!

Du bist jetzt bereit für eine **großartige Präsentation**!

Die Evil Twin Attacke ist ein spannendes und relevantes Thema.
Deine DHBW wird das Fachwissen und die praktische Demonstration lieben.

**Wichtig:**
- 💪 Selbstvertrauen! Du kennst das Thema!
- 🎯 Fokus auf Live Demo - das ist dein Unterscheidungsmerkmal!
- 🤝 Mit Partner kommunizieren - gemeinsam sind ihr stärker!
- ⏱️  Timing beachten - nicht hetzen, professionelles Tempo!

---

**Fragen? Alles notwendige ist in den Dateien dokumentiert.**

**Datei-Struktur:**
```
📁 EvilTwin/
  ├─ Evil_Twin_Presentation.pptx        (Die Präsentation!)
  ├─ PRAESENTATION_NOTIZEN.md           (Sprechzettel)
  ├─ DEMO_REFERENZKARTE.md              (Demo How-To)
  ├─ GESAMTKOMPENDIUM.md                (Kompletter Guide)
  ├─ VERGLEICH_DIAGRAMME.md             (Tiefergehend)
  └─ README.md                          (Diese Datei!)
```

**Du brauchst die Präsentation? → `Evil_Twin_Presentation.pptx`**
**Du brauchst Sprechnotizen? → `PRAESENTATION_NOTIZEN.md`**
**Du brauchst Demo-Help? → `DEMO_REFERENZKARTE.md`**
**Du brauchst alles zusammen? → `GESAMTKOMPENDIUM.md`**

---

*Erstellt mit ❤️ für DHBW Offensive Security Students*
*Version 1.0 | November 2024*

**Viel Erfolg und viel Spaß beim Präsentieren!** 🚀

