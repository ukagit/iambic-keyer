# Iambic keyer rp2040 include simple  transceiver on 40m 
#
# Copyright (C) 2022 dl2dbg
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.



from machine import Pin, Timer, PWM
from rp2 import PIO, StateMachine, asm_pio
import utime # utime is the micropython brother of time
import time
import ujson
 

#xiaoKey - a computer connected iambic keyer
# Copyright 2022 Mark Woodworth (AC9YW)
#https://github.com/MarkWoodworth/xiaokey/blob/master/code/code.py
          
# setup encode and decode
encodings = {}
def encode(char):
    global encodings
    if char in encodings:
        return encodings[char]
    elif char.lower() in encodings:
        return encodings[char.lower()]
    else:
        return ''
    
decodings = {}
def decode(char):
    global decodings
    if char in decodings:
        return decodings[char]
    else:
        return '('+char+'?)'

def MAP(pattern,letter):
    decodings[pattern] = letter
    encodings[letter ] = pattern
    
MAP('.-'   ,'a') ; MAP('-...' ,'b') ; MAP('-.-.' ,'c') ; MAP('-..'  ,'d') ; MAP('.'    ,'e')
MAP('..-.' ,'f') ; MAP('--.'  ,'g') ; MAP('....' ,'h') ; MAP('..'   ,'i') ; MAP('.---' ,'j')
MAP('-.-'  ,'k') ; MAP('.-..' ,'l') ; MAP('--'   ,'m') ; MAP('-.'   ,'n') ; MAP('---'  ,'o')
MAP('.--.' ,'p') ; MAP('--.-' ,'q') ; MAP('.-.'  ,'r') ; MAP('...'  ,'s') ; MAP('-'    ,'t')
MAP('..-'  ,'u') ; MAP('...-' ,'v') ; MAP('.--'  ,'w') ; MAP('-..-' ,'x') ; MAP('-.--' ,'y')
MAP('--..' ,'z')
              
MAP('.----','1') ; MAP('..---','2') ; MAP('...--','3') ; MAP('....-','4') ; MAP('.....','5')
MAP('-....','6') ; MAP('--...','7') ; MAP('---..','8') ; MAP('----.','9') ; MAP('-----','0')

MAP('.-.-.-','.') # period
MAP('--..--',',') # comma
MAP('..--..','?') # question mark
MAP('-...-', '=') # equals, also /BT separator
MAP('-....-','-') # hyphen
MAP('-..-.', '/') # forward slash
MAP('.--.-.','@') # at sign

          

class transceiver():
    
    '''
    dl2dbg 3.3.2022
    
    # StateMachine ....to trasmit cw with rp2040 pin
    #
    # doku
    # Cornell University ECE4760 
    # RP2040 testing
    # ttp://people.ece.cornell.edu/land/courses/ece4760/RP2040/index_rp2040_testing.html
    '''

    def __init__(self,tx_pin):
        self.tx_opt_pin = Pin(tx_pin,Pin.OUT)
        
        
        self.freq = 7005250 # auf 40m fangen wir an
        self.on_off = 1
        self.osc()
        
    def set_freq(self,frq):
        self.freq = frq
        self.osc()
        #print(frq)
        
    def on(self):
        self.on_off = 1
    def off(self):
        self.on_off = 0
        

    @asm_pio(set_init=PIO.OUT_LOW)

    def tx_toggle():
        wrap_target()
        set(pins, 1) [1]
        set(pins, 0) [1]
        wrap()
        
    def osc(self):
        
        self.sm3 = StateMachine(3, self.tx_toggle, freq= self.freq*4, set_base=Pin(2), jmp_pin=self.tx_opt_pin)
        self.sm3.active(0)
        self.sm3.active(1)
        
    def send(self,state):
        if self.on_off == 1:
            self.sm3.active(state)
        
        
class tx_opt():
    
    '''
    3.3.2022
    simple pin on/off for tx optocopler
    # 
    '''

   
    def __init__(self,tx_pin):
        self.tx_opt_pin = Pin(tx_pin,Pin.OUT)
        self.on_off = 1
        
        #self.tx_opt_pin = Pin(10, Pin.OUT)
        
    def on(self):
        self.on_off = 1
    def off(self):
        self.on_off = 0
        
    def send(self,state):
        if self.on_off == 1:
            self.tx_opt_pin.value(state)
        
    
    

class command_button():
    '''
    6.3.2020 button for Command request 
    '''

    def __init__(self,pin_button,led1,led2):
        #GPIO welcher als PWM Pin benutzt werden soll
        
        self.button =  Pin(pin_button,Pin.IN,Pin.PULL_UP)
        self.led1   =  Pin(led1, Pin.OUT)
        self.led2   =  Pin(led2, Pin.OUT)
        
        self.button_save = 0
        self.btimer = 0 # timer for debounce
        self.comannd_state = 1 # im keyer mode
#         
#         self.save_tfreq =  cwt.tonfreq()
#         self.ton_freq_command = cwt.tonfreq_command()
        
    def button_press(self):
        return(self.button.value())
    
    def button_command_off(self):
        self.comannd_state =  0
        self.led1(self.comannd_state)
        self.led2(self.comannd_state)
        
        text2cw("e")
             
        
    def button_state(self):
        if self.button.value() == 0 and self.button_save == 1: # 1 0 ->button is press
            utime.ticks_ms()
            self.btimer  = utime.ticks_ms()
            self.button_save = 0
            
        elif self.button.value() == 1 and self.button_save == 0 and utime.ticks_ms() > self.btimer + 10 : #0 0 ->button IS press
             self.button_save = 1
             
             self.led1(not self.comannd_state)
             self.comannd_state =  not self.comannd_state
             if self.comannd_state:
                     
                     cwt.set2cton()
             else :
                     cwt.set2ton()
                     
            
             text2cw("e")
             
        return(self.button_save)
            
    

        
class cw_sound():
    '''
    6.3.2020 simple sound with pwm 
    '''

    def __init__(self,pin=22):
        #GPIO welcher als PWM Pin benutzt werden soll
        self.pwm_ton = PWM(Pin(pin))
        #eine Frequenz von 1000hz also 1kHz
        self.freq = 600
        self.Ton_freq_command = 1500
        self.pwm_ton.freq(self.freq)
        self.cwvolum = 2000  #30000 laut
        self.on_off = 1
     

    def set_tonfreq(self,freq):
        self.freq = freq
        self.pwm_ton.freq(self.freq)##
        
    def set2ton(self):
        self.pwm_ton.freq(self.freq)
        
    def set2cton(self):
        self.pwm_ton.freq(self.Ton_freq_command)
        
    def tonfreq(self):
        return self.freq
    
    def tonfreq_command(self):
        return self.Ton_freq_command
       
        
    def volume(self,volume):
        self.cwvolum = volume
        

    def tone(self,on):
        if self.on_off == 1:
            if on:
                self.pwm_ton.duty_u16(self.cwvolum)
            else:
                self.pwm_ton.duty_u16(1)
                
    def onoff(self,state):
        self.on_off = state
    

def cw(state):
    cwt.tone(state)
    tx.send(state)
    txopt.send(state)
    
    
class cw_timing():
    def __init__(self,wpm=18):
        self.wpm = wpm
    # timing
    def dit_time(self):
        self.PARIS = 50 
        return 60.0 / self.wpm / self.PARIS *1000  ## mili sekunden
    
    def set_wpm(self, wpm):
        self.wpm = wpm



# decode iambic b paddles
class Iambic:
    """
Command
a -> Iambic Mode A
b -> Iambic Mode B
m -> request Iambic Mode A/B

? -> request value of ...

i -> TX_opt enable(on) disable(off)
j -> TX_transceiver enable(on) disable(off)
o -> Sidetone toggle (on) (off)

f -> adjust sidetone frequenz
v -> adjust sidetone volume 1-100
q -> adjust qrg of tx
w -> adjust WPM (Word per minute)

t -> tune mode, end with command mode
s -> save parameter to  file

x -> exit Command mode

tranceiver is toggle pin of rp2040
def tx_toggle():
        wrap_target()
        set(pins, 1) [1]
        set(pins, 0) [1]
        wrap()

qrg:
.... 7029870
.... 7023700
.... 7017540
.... 7011390
.... 7005250


"""
    
    def __init__(self,dit_key,dah_key):
        self.dit_key = Pin(dit_key,Pin.IN,Pin.PULL_UP)
        self.dah_key = Pin(dah_key,Pin.IN,Pin.PULL_UP)
      
        self.dit = False ; self.dah = False
        self.ktimer = 0
        self.ktimer_end = 0
        
        self.in_char = True 
        self.in_word = True
        self.char = ""

    
        
        self.IDLE=0; self.CHK_DIT=1; self.CHK_DAH=2; self.KEYED_PREP=3; self.KEYED=4; self.INTER_ELEMENT=5 
        self.keyerState = self.IDLE
        self.keyerControl = 0 #keyerControl = IAMBICB;      // Or 0 for IAMBICA
        
        #  keyerControl bit definitions
        self.DIT_L     = 0x01     # Dit latch
        self.DAH_L     = 0x02     #Dah latch
        self.DIT_PROC  = 0x04     # Dit is being processed
        self.PDLSWAP   = 0x08     # 0 for normal, 1 for swap
        #self.iambic_mode  = 0x10     # 0 for Iambic A, 1 for Iambic B
        self.LOW = 0
        self.HIGH = 1
        
        self.tune = 0 # transmit
        self.transmit_tune= 0
        
        self.adj_sidetone = 0
        self.adj_wpm = 0
        self.adj_qrg = 0
        self.adj_sidetone_volume = 0
        
# this variable are default an will be overwrite with the json file
#
        self.iambic_mode  = 0x10     # 0 for Iambic A, 1 for Iambic B
        self.wpm = 18 
        self.tx_enable = 0
        self.txt_enable = 0
        self.sidetone_enable = 1
        self.sidetone_freq = 700 #
        self.sidetone_volume = 10 # range 1,100 * 200 -> 2000 #30000 laut
#        
        
        self.f_liste =[7017540,7005250,7011390,7036050,7029870,7023700]
        self.f_liste.sort()
        
        self.qrg_marke = 0
        self.qrg = self.f_liste[self.qrg_marke]
        
        self.request = 0 # request of parameters 
        
#--------------
        self.iambic_data = {} # create date store
        
        if cb.button_press() == 1: # not press "0" -> json date read,and init, if "0" use factory setting 
            self.read_jsondata()
            self.init_iambic_data()  

    def set_data(self,key,value):
        #self.iambic_data
        self.key=key
        self.value= value
        self.iambic_data[self.key]=self.value
    #    print ('setting',menu_data)


    def write_data2file(self):
        #self.iambic_data
        self.json_string = ujson.dumps(self.iambic_data)

       
        with open('json_iambic.json', 'w') as outfile:
            ujson.dump(self.json_string, outfile)
            
    def read_jsondata(self):
        print("read json data")
        with open('json_iambic.json') as json_file:
            self.data = ujson.load(json_file)

        self.iambic_data = ujson.loads(self.data)
        
    def write_jsondata(self): # write new json file
        #print("write_jsondata")
        self.set_data("iambic_mode",self.iambic_mode) # transmit
        self.set_data("wpm",self.wpm)
        
        self.set_data("sidetone_enable",self.sidetone_enable)
        self.set_data("sidetone_freq",self.sidetone_freq)
        self.set_data("sidetone_volume",self.sidetone_volume)
          
        self.set_data("tx_enamble",self.tx_enable)
        self.set_data("txt_emable",self.txt_enable)
     
        self.write_data2file()
        
    
    def init_iambic_data(self): # is only use at the begin to create new json file
        
        self.iambic_mode = self.iambic_data["iambic_mode"]
        self.wpm = self.iambic_data["wpm"]
        
        self.sidetone_enable = self.iambic_data["sidetone_enable"]
        self.sidetone_freq    = self.iambic_data["sidetone_freq"]
        self.sidetone_volume  = self.iambic_data["sidetone_volume"]
        
        self.tx_enamble = self.iambic_data["tx_enamble"]
        self.txt_emable = self.iambic_data["txt_emable"]
        
        # set extern Parameter
        cw_time.set_wpm(self.wpm)
        cwt.set_tonfreq(self.sidetone_freq)
        cwt.volume(self.sidetone_volume*200)
        
        
        cwt.onoff(self.sidetone_enable)
        
        
#---------------         



    def update_PaddleLatch(self):


        if (self.dit_key.value() == self.LOW):
            self.keyerControl |= self.DIT_L
        if (self.dah_key.value() == self.LOW):
            self.keyerControl |= self.DAH_L
        
    def cycle(self):
        #utime.sleep(0.3)
        cb.button_state() ## Comand button abfragen
        
        if cb.comannd_state == 1 : # "1" ->comand mode
            
            if self.tune == 1: # begin tune
        
                self.keyerSate = self.IDLE
                
                if self.dah_key.value() == self.LOW: # transmit on
                    self.transmit_tune= 1
                    cw(1)
                elif self.dit_key.value() == self.LOW: #transmit off
                    self.transmit_tune= 0
                    cw(0)
                return
                
                
                
            elif self.adj_sidetone == 1: # begin tune
        
                self.keyerSate = self.IDLE
                
                if self.dah_key.value() == self.LOW: # transmit on
                    if self.sidetone_freq > 2000:
                        text2cw("max")
                    else:
                        self.sidetone_freq =self.sidetone_freq +10
                        cwt.set_tonfreq(self.sidetone_freq) # change the Freq
                        
                        play("-")
                elif self.dit_key.value() == self.LOW: #transmit off
                    if self.sidetone_freq < 50:
                        text2cw("min")
                    else:
                        self.sidetone_freq = self.sidetone_freq -10
                        cwt.set_tonfreq(self.sidetone_freq)
                        
                        play(".")
                return
             
            
            elif self.adj_sidetone_volume == 1: # adjust sidetone volume
        
                self.keyerSate = self.IDLE
                self.tx_enable = 1
                tx.on()
                
                if self.dah_key.value() == self.LOW: # transmit on
                    if self.sidetone_volume >= 100:
                        text2cw("max")
                    else:
                        self.sidetone_volume = self.sidetone_volume + 1
                        cwt.volume(self.sidetone_volume*200)
                        #print(self.sidetone_volume)
                        play("-")
                        
                elif self.dit_key.value() == self.LOW: #transmit off
                    if self.sidetone_volume <= 0:
                        text2cw("min")
                    else:
                        self.sidetone_volume = self.sidetone_volume - 1
                        cwt.volume(self.sidetone_volume*200)
                        #print(self.sidetone_volume)
                        play(".")
                return
            
            elif self.adj_wpm == 1: # begin tune
        
                self.keyerSate = self.IDLE
                
                if self.dah_key.value() == self.LOW: # transmit on
                    self.wpm = self.wpm+1
                    cw_time.set_wpm(self.wpm)
                    play("-")
                elif self.dit_key.value() == self.LOW: #transmit off
                    self.wpm = self.wpm+1
                    cw_time.set_wpm(self.wpm)
                    play(".")
                return
            
            elif self.adj_qrg == 1: # begin tune
        
                self.keyerSate = self.IDLE
                
                
                if self.dah_key.value() == self.LOW: # transmit on
                    if self.qrg_marke  >= len(self.f_liste)-1:
                        text2cw("max")
                    else:
                        self.qrg_marke = self.qrg_marke + 1
                        tx.set_freq(self.f_liste[self.qrg_marke])
                        print("....",self.f_liste[self.qrg_marke])
                        play("-")
                        
                elif self.dit_key.value() == self.LOW: #transmit off
                    if self.qrg_marke  <= 0:
                        text2cw("min")
                    else:
                        self.qrg_marke = self.qrg_marke - 1
                        tx.set_freq(self.f_liste[self.qrg_marke])
                        print("....",self.f_liste[self.qrg_marke])
                        play(".")
                return
     
                
                
                
        else: # wenn  commad mode ende dann auch tune :-)
            self.tune = 0
            self.adj_qrg = 0
            self.adj_sidetone = 0
            self.adj_wpm = 0
            self.adj_sidetone_volume = 0
            self.request = 0
                
            
        
        if self.keyerState == self.IDLE:
            # Wait for direct or latched paddle press
            
            if utime.ticks_ms() > (self.ktimer_end + cw_time.dit_time()*2):
                if self.in_char:
                    self.in_char = False
                    #print(utime.ticks_ms(),self.ktimer_end)
                    #print("char",self.char)
                   
                    if cb.comannd_state == 1: # "1" ->comand mode
                        Char = decode(self.char)
# comand mode ----------------                        
                        if  Char == "i" : # TX enable(on) disable(off)
                            if self.request == 1:
                                if self.tx_enable :
                                    text2cw("on")
                                else:
                                    text2cw("off")
                            else:    
                                self.tx_enable = not self.tx_enable
                                if self.tx_enable:
                                    txopt.on()
                                    text2cw("on")
                                else:
                                    text2cw("off")
                                    txopt.off()
                                #print("Transmit", self.tx_enable)
                                cb.button_command_off()
                                
                        elif  Char == "j" : # TX opt enable(on) disable(off)
                            if self.request == 1:
                                if self.txt_enable :
                                    text2cw("on")
                                else:
                                    text2cw("off")
                            else:    
                                self.txt_enable = not self.txt_enable
                                if self.txt_enable:
                                    tx.on()
                                    text2cw("on")
                                else:
                                    text2cw("off")
                                    tx.off()
                                #print("Transmit", self.txt_enable)
                                cb.button_command_off()
                                
                        elif  Char == "o" : # TX enable(on) disable(off)
                            if self.request == 1:
                                if self.sidetone_enable :
                                    text2cw("on")
                                else:
                                    text2cw("off")
                                    
                                
                            else:
                                self.sidetone_enable = not self.sidetone_enable
                                if self.sidetone_enable:
                                    cwt.onoff(1)
                                    text2cw("on")
                                else:
                                    text2cw("off")
                                    cwt.onoff(0)
                                    cb.button_command_off()
                                print("sidetone", self.tx_enable)
                                
                        elif  Char == "t" : # tune mode 
                            self.tune = 1
                            if self.tune:
                                text2cw("on")
                                
                        elif  Char == "w" : # WPM Change Speed ) 
                            if self.request == 1:
                                text2cw(str(self.wpm))
                            
                            else:
                                self.adj_wpm = 1   
                                if self.tune:
                                    text2cw("on")
                                    
                        elif  Char == "v" : # sidetone volume controll
                            if self.request == 1:
                                text2cw(str(self.sidetone_volume))
                                
                            else:
                                self.adj_sidetone_volume = 1
                            
                        elif  Char == "?" : # request of parameters
                            self.request = 1
                            
                        elif  Char == "x" : # command exit
                                
                                cb.button_command_off()
                                
                        elif  Char == "f" : # adjust sidetone frequenz
                            if self.request == 1:
                                text2cw(str(self.sidetone_freq))
                            else:
                                self.adj_sidetone = 1
                        
                        elif  Char == "q" : # adjust qrg
                            if self.request == 1:
                                text2cw(str(self.f_liste[self.qrg_marke]))
                            else:
                                self.adj_qrg = 1
                        
                        elif  Char == "m" : # Iambic mode a/b
                            if self.request == 1:
                                if self.iambic_mode== 16 : text2cw("b")
                                else : text2cw("a")
                            
                        elif  Char == "a" : # adjust sidetone frequenz                            
                                self.iambic_mode  = 0 #  0x10     # 0 for Iambic A, 1 for Iambic B
                                cb.button_command_off()
                                
                                self.write_jsondata() # save parameter afer change
                                
                        elif  Char == "s" : # adjust sidetone frequenz                            
                                self.write_jsondata() # save parameter afer change
                                text2cw("save")
                                cb.button_command_off()
                        
                                
                        elif  Char == "b" : # adjust sidetone frequenz
                                self.iambic_mode  = 0x10 #  0x10     # 0 for Iambic A, 1 for Iambic B
                                cb.button_command_off()
                             
                    else :
                        print(decode(self.char))
                    
                    self.char = ""
#                 #send(decode(self.char))
#                 self.char = ""
           
            if ((self.dit_key.value() == self.LOW) or (self.dah_key.value() == self.LOW) or (self.keyerControl & 0x03)):
                self.update_PaddleLatch()
                self.keyerState = self.CHK_DIT
                
        elif self.keyerState == self.CHK_DIT:
            #See if the dit paddle was pressed
            
            if (self.keyerControl & self.DIT_L):
                self.keyerControl |= self.DIT_PROC
                self.ktimer = cw_time.dit_time()
                self.keyerState = self.KEYED_PREP
                self.in_char = True 
                self.in_word = True
                self.char += "."
            else:
                self.keyerState = self.CHK_DAH;
                
        
        elif self.keyerState == self.CHK_DAH:
            #See if dah paddle was pressed
            
            if (self.keyerControl & self.DAH_L):
                self.ktimer = cw_time.dit_time()*3
                self.keyerState = self.KEYED_PREP
                self.in_char = True 
                self.in_word = True
                self.char += "-"
            else:
                self.keyerState = self.IDLE;
  
        elif self.keyerState == self.KEYED_PREP:
            #print("Prep")
            #Assert key down, start timing, state shared for dit or dah
            #digitalWrite(ledPin, HIGH);         // turn the LED on
            self.Key_state = self.HIGH
            cw(True)
            
            self.ktimer += utime.ticks_ms()                 # set ktimer to interval end time
            self.keyerControl &= ~(self.DIT_L + self.DAH_L)  # clear both paddle latch bits
            self.keyerState = self.KEYED                 # next state
        
        elif self.keyerState == self.KEYED:
            if (utime.ticks_ms() > self.ktimer): #are we at end of key down?
                self.Key_sate = 0
                cw(False)
                
                self.ktimer = utime.ticks_ms()+ cw_time.dit_time()  #inter-elemet time
                self.keyerState = self.INTER_ELEMENT #next state
            else:
                if (self.keyerControl & self.iambic_mode):
                    self.update_PaddleLatch()           # early paddle latch in Iambic B mode
        

                
        elif self.keyerState == self.INTER_ELEMENT:
            self.update_PaddleLatch() #latch paddle state
            if (utime.ticks_ms() > self.ktimer):         #are we at end of inter-space ?
                self.ktimer_end = utime.ticks_ms()
                if (self.keyerControl & self.DIT_PROC): # was it a dir or dah?
                    self.keyerControl &= ~(self.DIT_L + self.DIT_PROC) #clear two bits
                    self.keyerState = self.CHK_DAH  #dit done, check for dah
                    #print(utime.ticks_ms(),self.ktimer_end)
                else:
                    self.keyerControl &= ~(self.DAH_L) #clear dah latch
                    self.keyerState = self.IDLE        #go idle
            
            


# transmit pattern
def play(pattern):
    #print("play")
    for sound in pattern:
        if sound == '.':
            cw(True)
            #print(uutime.ticks_ms()())
            utime.sleep(cw_time.dit_time()/1000)
            #print(uutime.ticks_ms())
            cw(False)
            utime.sleep(cw_time.dit_time()/1000)
        elif sound == '-':
            cw(True)
            utime.sleep(3*cw_time.dit_time()/1000)
            cw(False)
            utime.sleep(cw_time.dit_time()/1000)
        elif sound == ' ':
            utime.sleep(4*cw_time.dit_time()/1000)
    utime.sleep(2*cw_time.dit_time()/1000)

def text2cw(str):
    for c in str:
        play(encode(c))
         
#----------------------------------------

# Setup Hardware pin on rp2040

comand_button    = 15 
onboard_led      = 25 
extern_led       = 3 
tx_opt_pin       = 10 
tx_pin           = 18 

cw_sound_pin     = 22
paddle_left_pin  = 17 
paddle_right_pin = 18 
#----------------------------------------
     
#paddle instance
print("keyer")

# user class 
tx      = transceiver(tx_pin)
txopt   = tx_opt(tx_opt_pin)

cwt = cw_sound(cw_sound_pin)

cw_time = cw_timing(18)
cb      = command_button(comand_button,onboard_led,extern_led)
iambic  = Iambic(paddle_left_pin,paddle_right_pin)

text2cw("r")
#-------- 
while True:
      iambic.cycle()
    
