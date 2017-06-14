# PyAvrControl

PyAvrControl is python library that facilitates the interaction with audio systems that implement
the [Denon AVR](https://usa.denon.com/us/product/hometheater/receivers) control protocol. This enables
a pythonistic approach to interacting with your AVR unit, as well as a comprehensive CLI for bash/powershell scripted
or one-off commands.

## Library

The DenonAvr object provides access to all controls. Althrough commands available are extensive, they are not complete.
There are certain commands that have not yet been implemented, but can be easely added, for example,
with a new DenonCommandConf object.

The DenonAvr commands are safe for multi-threading/processing applications as long as a single DenonAvr object is used
for this purpose, guaranteeing no race conditions or deadlocks, which can be further aligning with hardware's concurrency
capacity.

# Available high level abstractions

## DenonAvr Object
Command and controls multithread-safe object

Example:
```
from denon import DenonAvr

avr = DenonAvr('192.168.1.100')

avr.power.status()
['P', 'W', 'S', 'T', 'A', 'N', 'D', 'B', 'Y']
```

## DenonCommand Object

Command context manager for sending/recieving raw commands to the AVR unit

```
from denon import DenonCommand

with DenonCommand('192.168.1.100') as d:
  d.send('PW?')
  print(d.recieve())
```

## DenonCommandConf Object

Build custom command hierchy for a limited or expanded set of commands

```
from denon_cmds import (DenonCommandConf, cmd_main_pwr, cmd_sleep)

conf = DenonCommandConf(denon_cmds.cmd_main_pwr,
                        denon_cmds.cmd_sleep)
```

## Example Controls

```python
from denon import DenonAvr

avr = DenonAvr('192.168.1.100')

avr.power.status()
['P', 'W', 'S', 'T', 'A', 'N', 'D', 'B', 'Y']

avr.power.on()
['Z', 'M', 'O', 'N']

avr.volume.up()    # increase volume by 0.5db
['M', 'V', '2', '0', '5']

avr.volume.set(35) # set volume to 35.0db
['M', 'V', '3', '5', '0']

avr.audio_input.available()
['bd',
 'ipd',
 'iradio',
 'cd',
 'usb',
 'tv',
 'aux',
 'net',
 'flickr',
 'napster',
 'status',
 'pandora',
 'sat_cbl',
 'ipod',
 'dock',
 'game',
 'hdraido',
 'favorites',
 'lastfm',
 'rhapsody',
 'phono',
 'dvd',
 'server',
 'tunner',
 'dvr']

avr.audio_input.bd()
[]

avr.audio_input.status()
['S', 'I', 'B', 'D']
```

# CLI

The command line interface provides access to most AVR commands withouth having to intergrate any additional python code. 

```bash
pyton denon_cli.py --help

Usage: denon_cli.py <host> <command> <sub-command> <optional: param>
...
```

Example usage:

```bash
python denon_cli.py 192.168.1.100 audio_input tv
python denon_cli.py 192.168.1.100 volume status
```

For Complete list of available command use --help

Available Commands:

```
[Change audio signal type for current audio input]
audio_source:
              status
              auto
              analog
              hdmi
              digital

[Change video input source]
video_input:
             bd
             status
             sat_cbl
             tv
             dvd
             dock
             game
             source
             aux
             dvr
             game2

[Video monitor output configuration]
monitor:
         res_1080i
         res_1080p
         video_mode_movie
         aspect_status
         hdmi_audio_amp
         res_hdmi_auto
         aspect_normal
         res_hdmi_720p
         res_720p
         res_hdmi_status
         res_status
         hdmi_audio_status
         res_hdmi_1080p
         res_hdmi_480p
         hdmi_out1
         hdmi_out2
         video_mode_status
         video_mode_game
         res_hdmi_1080i
         hdmi_status
         res_480p
         res_auto
         aspect_full
         video_mode_auto
         hdmi_audio_tv

[Change power on/standby state]
power:
       standby
       on
       status

[Change the surround mode to specific type]
surround_mode:
               quick1
               mch_stereo
               quick3
               quick2
               quick5
               quick4
               direct
               mono_movie
               pure_direct
               matrix
               movie
               virtual
               music
               status
               standard
               game
               stereo
               dolby_digital
               rock_arena
               jazz_club
               video_game
               dts_surround

[Increase, decrease, mute or set specific volume]
volume:
        status
        set range:00-99
        mute
        unmute
        up
        down

[Change main-zone power state]
main_zone:
           status
           on
           off

[Change audio signal processing for current audio input]
audio_mode:
            dts
            auto
            status
            pcm

[Change audio input source]
audio_input:
             bd
             ipd
             iradio
             cd
             usb
             tv
             aux
             net
             flickr
             napster
             status
             pandora
             sat_cbl
             ipod
             dock
             game
             hdraido
             favorites
             lastfm
             rhapsody
             phono
             dvd
             server
             tunner
             dvr

[Increase, decrease, or set specific channel volume]
channel_volume:
                front_right_set range:38-62
                front_right_down
                front_left_down
                front_right_up
                sub_down
                front_wide_left_up
                sur_back_right_set range:38-62
                sur_right_set range:38-62
                surround_left_set range:38-62
                front_height_right_up
                sur_back_right_up
                front_left_set range:38-62
                front_height_right_down
                front_height_left_set range:38-62
                center_up
                front_wide_left_set range:38-62
                sur_back_right_down
                front_wide_left_down
                sur_right_down
                sur_right_up
                front_height_left_down
                sub_set range:38-62
                front_height_right_set range:38-62
                sub_up
                surround_left_up
                center_down
                front_wide_right_down
                front_wide_right_up
                front_left_up
                front_wide_right_set range:38-62
                front_height_left_up
                surround_left_down
                center_set range:38-62

[Set sleep state]
sleep:
       status
       set range:001-120
       off
```

## License

See the [GPL3](LICENSE.md) license.
