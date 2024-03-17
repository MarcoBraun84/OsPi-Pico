import time
time.sleep(2)
import machine
import uasyncio as asyncio
import lvgl as lv
from hal.ili9488 import Ili9488
from hal.xpt2046 import Xpt2046
from hal.adc08100 import Adc08100
from gui.display_driver_utils import Display_Driver
from gui.async_utils import Lv_Async
import scope

import gc
gc.collect()
gc.threshold( gc.mem_free() // 4 + gc.mem_alloc() )

import machine
machine.freq( 200_000_000 )

lcd_baudrate = 24_000_000
tsc_baudrate = 1_000_000
adc_frequency = 10_000_000
pwm_frequency = 1_000_000

spi_sck = machine.Pin( 10, machine.Pin.OUT )
spi_mosi= machine.Pin( 11, machine.Pin.OUT )
spi_miso= machine.Pin( 12, machine.Pin.IN   )
spi_dc  = machine.Pin( 8, machine.Pin.OUT )

lcd_rst = machine.Pin( 15, machine.Pin.OUT )
lcd_bl  = machine.Pin( 13, machine.Pin.OUT )
lcd_cs  = machine.Pin( 9, machine.Pin.OUT )
tsc_cs  = machine.Pin( 16, machine.Pin.OUT )

adc_sck = machine.Pin( 21 )
mux_sel = machine.Pin( 20 )
adc_db  = machine.Pin( 0 ) # 0..7 pins are used

trig_pin = machine.Pin( 18 )
trig_pwm = machine.PWM( trig_pin )

trig_pwm.freq( pwm_frequency )
trig_pwm.duty_u16( int(0xFFFF*1.024/3.3) )

# Calibration values
print( "tsc()" )
AX, BX = 0.2525,-29.545
AY, BY =-0.1744, 335.52
tsc = Xpt2046( tsc_baudrate, tsc_cs, spi_sck, spi_mosi, spi_miso, ax=AX, bx=BX, ay=AY, by=BY )

# Init lcd last one to start lvgl with SPI LCD baudrate
print( "lcd()" )
lcd = Ili9488( lcd_baudrate, lcd_cs, spi_sck, spi_mosi, spi_miso, spi_dc, lcd_rst, lcd_bl )

print( "adc()" )
adc = Adc08100( adc_frequency, adc_sck, adc_db )

print( "lvgl" )
display_driver = Display_Driver( 480, 320, lcd, tsc )

print( "build" )
scr = lv.obj()
my_scope = scope.Scope( scr, adc, trig_pwm, display_driver, 1024, 256 )#480-160 )
lv.scr_load( scr )

timer = lv.timer_create_basic()
timer.set_period( 50 )
timer.set_cb( lambda tmr: my_scope.process() )

print( "run" )
lva = Lv_Async( refresh_rate=20 )
asyncio.Loop.run_forever()

timer.set_cb( None )
