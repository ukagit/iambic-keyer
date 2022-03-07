# iambic keyer

electronic iambic keyer

with command funktion and request
tranceiver on board  

![schematic](./img/assembly.png)

It is a minimalist device based on:

The `code` directory has the files to be installed on the *Seeed Xiao* device.

now `pcb` board simple soldering connectors on rp2040, and or assembly it a box

## Features

Command
* a -> Iambic Mode A
* b -> Iambic Mode B
* m -> request Iambic Mode A/B

* ? -> request value of ...

* i -> TX_opt enable(on) disable(off)
* j -> TX_transceiver enable(on) disable(off)
* o -> Sidetone toggle (on) (off)

* f -> adjust sidetone frequenz
* v -> adjust sidetone volume 1-100
* q -> adjust qrg of tx
* w -> adjust WPM (Word per minute)

* t -> tune mode, end with command mode
* s -> save parameter to  file

* x -> exit Command mode

## simpel HF tranceiver 
toggle pin of rp2040

simpel code
def tx_toggle():
        wrap_target()
        set(pins, 1) [1]
        set(pins, 0) [1]
        wrap()

you can receive the cw signal on qrg:
* .... 7029870
* .... 7023700
* .... 7017540
* .... 7011390
* .... 7005250
 

## Software Installation

1. Install Thonny latest version.
2. connect to a Raspberry Pi Pico
3. copy imabic_keyer_rp2040.py and json_iambic.json to rp2040
4. open the file imabic_keyer_rp2040.py and test the keyer
5. when all ok save the program as main.py

6. is the  json file wrong, you an start in factor mode, press command-button at boot time.



## Configuration
Main Paramter are setup in json file.
* "{
* \"txt_emable\": 0,
* \"sidetone_volume\": 10,
* \"sidetone_freq\": 700,
* \"sidetone_enable\":1,
* \"tx_enamble\": 0,
* \"iambic_mode\": 16,
* \"wpm\": 18
* }"

## Pinout

Setup Hardware pin on rp2040

comand_button    = 15 
onboard_led      = 25 
extern_led       = 3 
tx_opt_pin       = 10 
tx_pin           = 18 

cw_sound_pin     = 22
paddle_left_pin  = 17 
paddle_right_pin = 18


## Schematic

![schematic](./img/xiaokey.png)

## Assembly and Bill of Materials


KIS -> keep it simple

* J2 2.5mm  jack (for keyer, headphone)
* optocoupler for Tranceiver connect
* Button for coammdnmode
* option for externel coammnd led

## Future

Some Ideas / obtions on demand:

* power save mode
* wpm conrol with potentiometer

## References

MarkWoodworth xiaokey [Here](https://github.com/MarkWoodworth/xiaokey) 
