Es existieren 3 verschiedene Softwareversionen:\
### original_fixed
Die vollständige Originalsoftware, so abgeändert dass main.py und scope.py fehlerfrei laufen\
(Behebung lv.color_SIZE und zu großer Speicherbedarf) \

### simple_test.py
Dieses kurze Skript liest die Daten der Datenbus Pins per normalem Code und gibt diese auf dem Terminal aus, zusätzlich wird ein passende Clock Signal generiert.\
Dient nur zu simplen Testzwecken \

### measure_only
Entpsricht dem Originalcode, jedoch wurde alles was mit der Nutzeroberfläche oder demm Display zutun hat entfernt. Dient der reinen Analogwertaufnahme (wenn funktional implementiert) \

---

Bei den .uf2 Datein ahndelt es sich um Firmwaredatein für den Pi Pico, einerseits der normalen Micropython Firmware und 2 Micropython Firmware Datein in die die LVGL Bibliothek für Micropython integriert wurde.\
Der Code ist nur mit LVGL Version 8 kompatibel.
