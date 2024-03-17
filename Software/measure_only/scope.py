import os
import time
import machine
import rp2
import array
import uctypes

from hal.dma import DMA
from hal.adc08100 import Adc08100
from hal.trigger import Trigger


def foo2( sps, buf, rising, pre, post ):

    db  = machine.Pin( 0 ) # out
    sck = machine.Pin( 26 ) # side 0
    mux = machine.Pin( 27 ) # side 0
    trig = machine.Pin( 28, machine.Pin.IN, machine.Pin.PULL_DOWN ) # trigger
    #trig = machine.Pin( 19, machine.Pin.IN, machine.Pin.PULL_DOWN ) # trigger

    buf_addr_aligned = (uctypes.addressof( buf )+0xFF)&0xFFFFFF00
    buf_offset_aligned = buf_addr_aligned - uctypes.addressof( buf )

    t0 = time.ticks_us()
    adc = Adc08100( sps, mux, db, use_trigger=True )
    t1 = time.ticks_us()

    t0 = time.ticks_us()
    adc.dma.config(
        Adc08100.PIO0_BASE_RXF0, 
        buf_addr_aligned,
        0xFFFFFFFF,
        src_inc=False,
        dst_inc=True,
        trig_dreq=DMA.DREQ_PIO0_RX0,
        ring_sel=True,
        ring_size_pow2=8
    )
    t1 = time.ticks_us()

    t0 = time.ticks_us()
    adc.dma.enable()
    adc.sm.active( True )
    t1 = time.ticks_us()

    t0 = time.ticks_us()    
    trigger = Trigger( sps, trig, rising )
    t1 = time.ticks_us()

    DMA1_TRIG = 0x50000000 + 1 * 0x40 + 0x0C

    t0 = time.ticks_us()    
    trans_count0 = machine.mem32[ adc.dma.CHx_TRANS_COUNT ]
    trigger.read( pre, post, DMA1_TRIG )
    trans_count1 = machine.mem32[ adc.dma.CHx_TRANS_COUNT ]
    t1 = time.ticks_us()

    t0 = time.ticks_us()    
    adc.dma.disable()
    adc.sm.active( False )
    t1 = time.ticks_us()

    trans_count_diff = trans_count0 - trans_count1 # - 1

    
    trans_count_diff = trans_count_diff&0xFF

    return buf_offset_aligned, trans_count_diff


class Scope:
    def __init__( self, parent, adc, trig, len_sample, point_count ):
        self.parent = parent
        self.adc = adc
        self.trig = trig
        
        self.run = False
        self.single = False

        self.horizontal_scale = 1
        self.horizontal_position = 0

        self.channel1_scale = 1
        self.channel1_position = 0
        self.channel2_scale = 1
        self.channel2_position = 0
        self.channel1_selected = True

        self.trigger_channel1 = True
        self.trigger_edge = False
        self.trigger_auto = False
        self.trigger_position = 0

        self.chart = None
        
        self.context = []
        self.widgets = {}
        print( "build_ui" )
        
        self.len_sample = len_sample
        self.point_count = point_count
        self.buf_adc_a = bytearray( 512 )#self.len_sample + self.point_count )
        self.buf_adc_b = bytearray( 512 )#self.len_sample + self.point_count )
        self.adc_used = 0
        self.trigger_pos_a = 0
        self.trigger_pos_b = 0
        self.buf_adc_a_align = 0
        self.buf_adc_b_align = 0
        
        self.count_start = 0
        self.count_end = 0

        self.params = array.array( "I", [0 for n in range( 13 )] )
        print( "build_ui done" )
    
    def test_init( self, dst_buf, only_dma=False ):
        pass
    
    def test( self, dst_buf, delay_pre, delay_post, cb_enable=False ):
        pass
    
    def process( self ):
        
        scope_run = True
        trigger_edge = True
        hs = self.horizontal_scale
        hp = self.horizontal_position
        sps = [
            1_000_000,
            2_000_000,
            5_000_000,
            10_000_000,
            20_000_000,
            50_000_000,
            100_000_000,
        ][hs]
        
        if( scope_run or self.single ):
            self.single = False
            if( self.adc_used == 0 ):
                self.adc_used = 1
                t0 = time.ticks_us()
                #sps = 1_000_000
                self.buf_adc_a_align, self.trigger_pos_a = foo2( sps, self.buf_adc_a, trigger_edge, 1024, hp+128 )
                t1 = time.ticks_us()
                print( "aaaa", t1-t0 )
                #time.sleep_ms( 100 )
                t0 = time.ticks_us()

                self.params[0] = 10+32
                self.params[1] = 32
                
                self.params[2] = uctypes.addressof( self.buf_adc_a )
                self.params[3] = ((uctypes.addressof( self.buf_adc_a )+0xFF)&0xFFFFFF00)-uctypes.addressof( self.buf_adc_a )
                self.params[4] = self.trigger_pos_a
                self.params[5] = 0x001F
                
                self.params[6] = uctypes.addressof( self.buf_adc_b )
                self.params[7] = ((uctypes.addressof( self.buf_adc_b )+0xFF)&0xFFFFFF00)-uctypes.addressof( self.buf_adc_b )
                self.params[8] = self.trigger_pos_b
                self.params[9] = 0xFFFF
                
                self.params[10] = 256
                self.params[11] = 0xFF
                
                self.params[12] = 12
                #for i in range( 13 ):
                #    print( i, "0x{:08X}".format( self.params[i] ) )
                t1 = time.ticks_us()
                print( "bbbb", t1-t0 )
            else:
                self.adc_used = 0

                t0 = time.ticks_us()
                #sps = 1_000_000
                self.buf_adc_b_align, self.trigger_pos_b = foo2( sps, self.buf_adc_b, trigger_edge, 1024, hp+128 )
                t1 = time.ticks_us()
                print( "cccc", t1-t0 )

                t0 = time.ticks_us()
                self.params[0] = 10+32
                self.params[1] = 32
                
                self.params[2] = uctypes.addressof( self.buf_adc_b )
                self.params[3] = ((uctypes.addressof( self.buf_adc_b )+0xFF)&0xFFFFFF00)-uctypes.addressof( self.buf_adc_b )
                self.params[4] = self.trigger_pos_b
                self.params[5] = 0x001F
                
                self.params[6] = uctypes.addressof( self.buf_adc_a )
                self.params[7] = ((uctypes.addressof( self.buf_adc_a )+0xFF)&0xFFFFFF00)-uctypes.addressof( self.buf_adc_a )
                self.params[8] = self.trigger_pos_a
                self.params[9] = 0xFFFF
                
                self.params[10] = 256
                self.params[11] = 0xFF
                
                self.params[12] = 12
                t1 = time.ticks_us()
                print( "dddd", t1-t0 )
    
    def cb_single( self ):
        self.single = True
        print( "single", self.single )
    
    def cb_save( self ):
        idx = len( [name for name in os.listdir() if "data" in name] )
        fl_name = "data{}.txt".format( idx )
        
        if( self.adc_used == 1 ):
            buf_adc = self.buf_adc_a
            addr = uctypes.addressof( self.buf_adc_a )
            align = ((addr+0xFF)&0xFFFFFF00)-addr
            trigger = self.trigger_pos_a
        else:
            buf_adc = self.buf_adc_b
            addr = uctypes.addressof( self.buf_adc_b )
            align = ((addr+0xFF)&0xFFFFFF00)-addr
            trigger = self.trigger_pos_b
        
        with open( fl_name, "w" ) as fl:
            for i in range( 256 ):
                print(buf_adc[ align + ((trigger + i)&0xFF) ] )
                #fl.write( "{}\n".format( buf_adc[ align + ((trigger + i)&0xFF) ] ) )
        
                        
                        

