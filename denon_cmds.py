"""
This file is part of PyAvrControl.

PyAvrControl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyAvrControl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyAvrControl.  If not, see <http://www.gnu.org/licenses/>.
"""


class _CommandStore(object):

  """
  Maintain a Denon AVR command hierarchy
  """
  def __init__(self):
    self._data_dict = {}

  def __getitem__(self, key):
    if key in self._data_dict:
      return self._data_dict[key]
    raise KeyError(key)

  def __call__(self):
    return self.available()

  def __iter__(self):
    for child in self.available():
      yield self.__dict__[child]

  def _insert(self, command, register):
    self._data_dict[command] = register
    self.__dict__[command] = self._data_dict[command]

  def get(self, key):
    if key in self._data_dict:
      return self._data_dict[key]

  def available(self):
    return self._data_dict.keys()


class _CommandInfo(object):

  def __init__(self, name, parent, cmd, params=None):
    self.parent = parent
    self.name = name
    self.cmd = cmd
    self.params = params
    self._call = None
    self._desc = None

  def __call__(self, *args, **kwargs):
    if self._call is not None:
      return self._call(*args, **kwargs)


class DenonCommandConf(_CommandStore):

  def __init__(self, *args):
    """
    Use CommandDict to build a command hierchy
    cmd_source -- denon api cmd dict
                  ex. { category: name: [command, param] }
    """
    self._data_dict = {}
    for cmd_dict in args:
      for tree_key, tree_val in cmd_dict.items():
        self._insert(tree_key, _CommandStore())
        for sub_key, sub_val in tree_val.items():
          if sub_key in ['_desc']:
            self.__dict__[tree_key].description = sub_val
            continue
          param = None
          if len(sub_val) > 1:
            param = sub_val[-1]
          call = sub_val[0]
          self.__dict__[tree_key]._insert(sub_key, _CommandInfo(sub_key,
                                                                tree_key,
                                                                call,
                                                                param))

"""
Denon AVR protocol commands

Documention:
http://openrb.com/wp-content/uploads/2012/02/AVR3312CI_AVR3312_PROTOCOL_V7.6.0.pdf

Note: This is an incomplete map of possible commands. More commands can be added
      as defined in the AVR PROTOCOL doc.

Note: No guarantee that all In-Command AVRs will support all the
      available commands.
"""

# Volume controls
# Page 7 and 8, v7.6.0
cmd_vol = {
  'volume': { 
    'up':     [ 'MVUP' ],
    'down':   [ 'MVDOWN' ],
    'set':    [ 'MV', 'range:00-99' ],
    'mute':   [ 'MUON' ],
    'unmute': [ 'MUOFF' ],
    'status': [ 'MV?' ],
    '_desc': 'Increase, decrease, mute or set specific volume'
  }
}

# Channel volume controls
# Page 7 and 8, v7.6.0
cmd_channel_vol = {
  'channel_volume': { 
    'front_left_up': [ 'CVFL UP' ],
    'front_left_down': [ 'CVFL DOWN' ],
    'front_left_set': [ 'CVFL', 'range:38-62' ],
    'front_right_up': [ 'CVFR UP' ],
    'front_right_down': [ 'CVFR DOWN' ],
    'front_right_set': [ 'CVFR', 'range:38-62' ],
    'center_up': [ 'CVC UP' ],
    'center_down': [ 'CVC DOWN' ],
    'center_set': [ 'CVC', 'range:38-62' ],
    'sub_up': [ 'CVSW UP' ],
    'sub_down': [ 'CVSW DOWN' ],
    'sub_set': [ 'CVSW', 'range:38-62' ],
    'surround_left_up': [ 'CVSL UP' ],
    'surround_left_down': [ 'CVSL DOWN' ],
    'surround_left_set': [ 'CVSL', 'range:38-62' ],
    'sur_right_up': [ 'CVSR UP' ],
    'sur_right_down': [ 'CVSR DOWN' ],
    'sur_right_set': [ 'CVSR', 'range:38-62' ],
    'sur_back_right_up': [ 'CVSR UP' ],
    'sur_back_right_down': [ 'CVSR DOWN' ],
    'sur_back_right_set': [ 'CVSR', 'range:38-62' ],
    'front_height_left_up': [ 'CVFHL UP' ],
    'front_height_left_down': [ 'CVFHL DOWN' ],
    'front_height_left_set': [ 'CVFHL', 'range:38-62' ],
    'front_height_right_up': [ 'CVFHR UP' ],
    'front_height_right_down': [ 'CVFHR DOWN' ],
    'front_height_right_set': [ 'CVFHR', 'range:38-62' ],
    'front_wide_left_up': [ 'CVFWL UP' ],
    'front_wide_left_down': [ 'CVFWL DOWN' ],
    'front_wide_left_set': [ 'CVFWL', 'range:38-62' ],
    'front_wide_right_up': [ 'CVFWR UP' ],
    'front_wide_right_down': [ 'CVFWR DOWN' ],
    'front_wide_right_set': [ 'CVFWR', 'range:38-62' ],
    '_desc': 'Increase, decrease, or set specific channel volume'
  }
}

# Main unit power controls (independent of zone specific power controls)
# Page 7, v7.6.0
cmd_main_pwr = {
  'power': {
    'on': [ 'PWON' ],
    'standby': [ 'PWSTANDBY' ],
    'status': [ 'PW?' ],
   '_desc': 'Change power on/standby state'
  }
}

# Main zone power controls
# Page 9, v7.6.0
cmd_zone_pwr = {
  'main_zone': { 
    'on': [ 'ZMON' ],
    'off': [ 'ZMOFF' ],
    'status': [ 'ZM?' ],
    '_desc': 'Change main-zone power state'
  }
}

# Power timeout/sleep settings
# Page 10, v7.6.0
cmd_sleep = {
  'sleep': {
    'off': [ 'SLPOFF' ],
    'set': [ 'SLP', 'range:001-120' ],
    'status': [ 'SLP?' ],
    '_desc': 'Set sleep state'
  }
}

# Audio input sources
# Page 8 and 9, v7.6.0
cmd_audio_input = {
  'audio_input': {
    'phono': [ 'PHONO' ],
    'cd': [ 'SICD' ],
    'tunner': [ 'SITUNNER' ],
    'dvd': [ 'SIDVD' ],
    'bd': [ 'SIBD' ],
    'tv': [ 'SITV' ],
    'sat_cbl': [ 'SISAT' ],
    'dvr': [ 'SIDVR' ],
    'game': [ 'SIGAME' ],
    'aux': [ 'SIV.AUX' ],
    'dock': [ 'SIDOCK' ],
    'hdraido': [ 'SIHDRAIO' ],
    'ipod': [ 'SIIPOD' ],
    'net':  [ 'SINET' ],
    'rhapsody': [ 'SIRHAPSODY' ],
    'napster': [ 'SINAPSTER' ],
    'pandora': [ 'SIPANDORA' ],
    'lastfm': [ 'SILASTFM' ],
    'flickr': [ 'SIFLICKR' ],
    'favorites': [ 'SIFAVORITES' ],
    'iradio': [ 'SIIRADIO' ],
    'server': [ 'SISERVER' ],
    'ipod': [ 'SIUSB/IPOD' ],
    'usb': [ 'SIUSB' ],
    'ipd': [ 'SIIPD' ],
    'status': [ 'SI?' ],
    '_desc': 'Change audio input source'
  }
}

# Change audio source type for specific audio input
# Page 10, v7.6.0
cmd_audio_source = {
  'audio_source': {
    'auto': [ 'SDAUTO' ],
    'hdmi': [ 'SDHDMI' ],
    'digital': [ 'SDDIGITAL' ],
    'analog': [ 'SIANALOG' ],
    'status': [ 'SI?' ],
    '_desc': 'Change audio signal type for current audio input'
  }
}

# Audio signal mode
# Page 10, v7.6.0
cmd_audio_mode = {
  'audio_mode': {
    'auto': [ 'DCAUTO' ],
    'dts': [ 'DCDTS' ],
    'pcm': [ 'DCPCM' ],
    'status': [ 'DC?' ],
    '_desc': 'Change audio signal processing for current audio input'
  }
}

# Video input source
# Page 10, v7.6.0
cmd_video_input = {
  'video_input': { 
    'dvd': [ 'SVDVD' ],
    'bd': [ 'SVBD' ],
    'tv': [ 'SVTV' ],
    'sat_cbl': [ 'SVSAT/CBL' ],
    'dvr': [ 'SVDVR' ],
    'game': [ 'SVGAME' ],
    'game2': [ 'SVGAME2' ],
    'aux': [ 'SVV.AUX' ],
    'dock': [ 'SVDOCK' ],
    'source': [ 'SVSOURCE' ],
    'status': [ 'SV?' ],
    '_desc': 'Change video input source'
  }
}

# Surround mode
# Page 11, v7.6.0
# Note: "quick memory" not implemented 
cmd_surround_mode = {
  'surround_mode': { 
     'movie': [ 'MSMOVIE' ],
     'music': [ 'MSMUSIC' ],
     'game': [ 'MSGAME' ],
     'direct': [ 'MSDIRECT' ],
     'pure_direct': [ 'MSPURE DIRECT' ],
     'stereo': [ 'MSSTEREO' ],
     'standard': [ 'MSSTANDARD' ],
     'dolby_digital': [ 'MSDOLBY DIGITAL' ],
     'dts_surround': [ 'MSDTS SURROUND' ],
     'mch_stereo': [ 'MSMCH STEREO' ],
     'rock_arena': [ 'MSROCK ARENA' ],
     'jazz_club': [ 'MSJAZZ CLUB' ],
     'mono_movie': [ 'MSMONO MOVIE' ],
     'matrix': [ 'MSMATRIX' ],
     'video_game': [ 'MSVIDEO GAME' ],
     'virtual': [ 'MSVIRTUAL' ],
     'status': [ 'MS?' ],
     'quick1': [ 'MSQUICK1' ],
     'quick2': [ 'MSQUICK2' ],
     'quick3': [ 'MSQUICK3' ],
     'quick4': [ 'MSQUICK4' ],
     'quick5': [ 'MSQUICK5' ],
     '_desc': 'Change the surround mode to specific type'
  }
}

# Configure video output
# Page 11 and 12, v7.6.0
cmd_hdmi_monitor = {
  'monitor': {
    'hdmi_out1': [ 'VSMONI1' ],
    'hdmi_out2': [ 'VSMONI2' ],
    'hdmi_status': [ 'VSMONI ?' ],
    'aspect_normal': [ 'VSASPNRM' ],
    'aspect_full': [ 'VSASPFUL' ],
    'aspect_status': [ 'VSASP ?'],
    'res_480p': [ 'VSSC48p' ],
    'res_1080i': [ 'VSSC10I' ],
    'res_720p': [ 'VSSC72P' ],
    'res_1080p': [ 'VSSC10P' ],
    'res_auto': [ 'VSSCAUTO' ],
    'res_status': [ 'VSSC ?'],
    'res_hdmi_480p': [ 'VSSCH48P' ],
    'res_hdmi_1080i': [ 'VSSCH10I' ],
    'res_hdmi_720p': [ 'VSSCH72P' ],
    'res_hdmi_1080p': [ 'VSSCH10P' ],
    'res_hdmi_auto': [ 'VSSHCAUTO' ],
    'res_hdmi_status': [ 'VSSCH ?' ],
    'hdmi_audio_amp': [ 'VSAUDIO AMP' ],
    'hdmi_audio_tv': [ 'VSAUDIO TV' ],
    'hdmi_audio_status': [ 'VSAUDIO ?'],
    'video_mode_auto': [ 'VSVPMAUTO' ],
    'video_mode_game': [ 'VSVPMGAME' ],
    'video_mode_movie': [ 'VSVPMMOVI' ],
    'video_mode_status': [ 'VSVPM ?'],
    '_desc': 'Video monitor output configuration'
  }
}

commands = DenonCommandConf(cmd_vol,
                            cmd_channel_vol,
                            cmd_main_pwr,
                            cmd_zone_pwr,
                            cmd_sleep,
                            cmd_audio_input,
                            cmd_audio_source,
                            cmd_audio_mode,
                            cmd_video_input,
                            cmd_surround_mode,
                            cmd_hdmi_monitor)

