import time
time.sleep(2)
import machine
import uasyncio as asyncio
from hal.adc08100 import Adc08100
import scope

import gc
gc.collect()
gc.threshold( gc.mem_free() // 4 + gc.mem_alloc() )

import machine
machine.freq( 200_000_000 )

adc_frequency = 1_000_000
pwm_frequency = 1_000_000


adc_sck = machine.Pin( 26 )
mux_sel = machine.Pin( 27 )
adc_db  = machine.Pin( 0 ) # 0..7 pins are used

trig_pin = machine.Pin( 8 )
trig_pwm = machine.PWM( trig_pin )

trig_pwm.freq( pwm_frequency )
trig_pwm.duty_u16( int(0xFFFF*1.024/3.3) )

print( "adc()" )
adc = Adc08100( adc_frequency, adc_sck, adc_db )

print( "Messung")
my_scope = scope.Scope(adc, trig_pwm, 1, 1024, 256 )#480-160 )
        

print( "run" )

