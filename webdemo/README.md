# Evil Twin · Interaktive Live-Demo (Webseite)

Eine eigenständige, interaktive Visualisierung des Evil-Twin-Angriffs für die
Präsentation. Läuft **vollständig lokal im Browser** – es wird nichts
gesendet, kein echtes Gerät angesprochen und keine echte Zugangsdaten
verarbeitet. Kein Internetzugang, kein Server, kein Build-Schritt nötig.

## Starten

Einfach **`index.html`** doppelklicken bzw. im Browser öffnen (Chrome, Edge,
Firefox, Safari). Für eine saubere URL in der Adressleiste geht alternativ:

```bash
cd webdemo
python3 -m http.server 8000
# dann im Browser: http://localhost:8000
```

## Was die Demo zeigt

8 Schritte, Schritt für Schritt oder per Autoplay abspielbar:

1. **Ausgangslage** – Client ist mit dem legitimen Access Point verbunden.
2. **Angreifer klont den Netznamen** – zweiter AP mit identischer SSID.
3. **Deauthentication** *(optional abschaltbar)* – bei WPA2 wirksam, bei
   WPA3 + PMF wird der Frame sichtbar abgewiesen.
4. **Erneuter Scan** – beide Netze erscheinen mit einstellbarer Signalstärke.
5. **Verbindungswahl** – das Gerät verbindet sich automatisch mit dem
   stärkeren Signal, unabhängig vom Betreiber.
6. **Portal / Phishing-Seite** *(optional abschaltbar)* – Handy-Mockup zeigt
   je nach Verbindung das reguläre oder das gefälschte Portal.
7. **Man-in-the-Middle** – HTTP sichtbar im Klartext, HTTPS bleibt inhaltlich
   geschützt.
8. **Erkennung & Abwehr** – WIDS-Sensor meldet die doppelte SSID.

## Bedienfeld (links)

- **SSID** frei editierbar
- **BSSIDs** per Zufall neu auswürfeln (Knopf), zeigt Angreifer-Nähe zur
  Original-Adresse
- **Sicherheitsmodus**: Offen / WPA2 / WPA3 + PMF – verändert das Verhalten
  des Deauth-Schritts direkt
- **Signalstärke-Regler** für beide Access Points – bestimmt, wem sich das
  Gerät in Schritt 5 anschließt (auch der Fall „legitimer AP gewinnt“ ist
  bewusst vorgesehen, inklusive passendem Hinweistext)
- **Deauth-/Portal-Schritt** einzeln ein-/ausblendbar – Stepleiste passt sich
  automatisch an
- **Präsentationsmodus** (oben rechts) blendet das Bedienfeld aus, für den
  Beamer

## Tastaturkürzel

`→` nächster Schritt · `←` vorheriger Schritt · `Leertaste` Play/Pause

## Technik

Reines HTML/CSS/JavaScript ohne Abhängigkeiten, ohne Frameworks, ohne
Internetzugriff (Systemschriftart, eingebettetes DHBW-Logo als PNG). Die
Netzwerk-Topologie ist eine live aktualisierte SVG-Grafik mit animierten
Paket-Flügen; Handy-Mockup und Frame-Log sind reines HTML/CSS.
