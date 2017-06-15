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


import os
import sys

from denon_cmds import commands, DenonCommandConf
from denon import DenonAvr


class DenonAvrCLI(object):

  @staticmethod
  def show_short_help():
    sys.stderr.write('Usage: %s <host> <command> <sub-command> <optional: param>\n' % sys.argv[0])
    sys.stderr.write('Examples:\n')
    sys.stderr.write('          %s 192.168.1.111 power status\n' % sys.argv[0])
    sys.stderr.write('          %s 192.168.1.111 volume set 35\n' % sys.argv[0])
    sys.stderr.write('          %s 192.168.1.111 audio_input dvd\n' % sys.argv[0])

  @staticmethod
  def show_help():
    sys.stderr.write('\nAvailable Commands:\n')
    for category in commands.available():
      sys.stderr.write('\n[%s]\n' % commands[category].description)
      sys.stderr.write('%s:\n' % category)
      for cmd in commands[category]:
        if cmd.params is not None:
          sys.stderr.write('  %s%s %s\n' % ((' ' * len(category)), cmd.name, cmd.params))
        else:
          sys.stderr.write('  %s%s\n' % ((' ' * len(category)), cmd.name))

  @staticmethod
  def parse_help():
    for h in [ '-help', '--help', 'help' ]:
      if h in sys.argv:
        DenonAvrCLI.show_short_help()
        DenonAvrCLI.show_help()
        sys.exit(0)

  def parse(self):
    try:
      set_host = sys.argv[1]
      set_group = sys.argv[2]
      set_cmd = sys.argv[3]
      set_param = None
      if commands[set_group][set_cmd].params:
        set_param = DenonCommandConf.param_parser(sys.argv[4], commands[set_group][set_cmd].params)
    except (IndexError, KeyError) as e:
      sys.stderr.write('Invalid arguments: %s (try --help)\n' % ' '.join(sys.argv[1:]))
      DenonAvrCLI.show_short_help()
      sys.exit(1)
    avr = DenonAvr(set_host)
    if set_param is not None:
      if set_param == False:
        sys.stderr.write('Invalid paramter: %s (try --help)\n' % ' '.join(sys.argv[1:]))
        return None
      else:
        cmd_out = avr[set_group][set_cmd](set_param)
    else:
      cmd_out = avr[set_group][set_cmd]()
    if cmd_out is not None:
      sys.stdout.write('%s\n' % ''.join(cmd_out))


if __name__ == '__main__':
  DenonAvrCLI.parse_help()
  cli = DenonAvrCLI()
  cli.parse()

