from machine import Pin, Timer
import time

# Definieren Sie die Pins, die für den parallelen Datenbus verwendet werden
pins = [Pin(i, Pin.IN) for i in range(8)]

# Definieren Sie den Pin für das Clock-Signal
clock = Pin(26, Pin.OUT)

# Erstellen Sie einen Timer
timer = Timer()

def toggle_clock(timer):
    clock.toggle()

# Konfigurieren Sie den Timer, um das Clock-Signal zu erzeugen
timer.init(freq=100000, mode=Timer.PERIODIC, callback=toggle_clock)

def read_adc():
    # Lesen Sie die Daten von jedem Pin und kombinieren Sie sie zu einem einzigen Wert
    value = 0
    for i in range(8):
        value |= (pins[i].value() << i)
    return value

while True:
    value = read_adc()
    print("ADC-Wert:", value)
    time.sleep(0.1)
