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


import codecs
import os
import socket
import sys
import time

from multiprocessing import Process, queues
from threading import Semaphore
from denon_cmds import commands

VERSION = '1.0.1'

_CONCURRENT = 1


class DenonAvrException(Exception): pass

class DenonAvrConnectException(Exception): pass

class _DenonCommandFunnel(object):

  def __init__(self, lock=Semaphore(_CONCURRENT)):
    self.lock = lock

  def __call__(self, func):
    def _execute(*args, **kwargs):
      self.lock.acquire()
      try:
        r = func(*args, **kwargs)
      except Exception as e:
        self.lock.release()
        raise e
      self.lock.release()
      return r
    return _execute


class DenonAvr(object):

  funnel = _DenonCommandFunnel()

  def __init__(self, host, port=23):
    self.host = host
    self.port = port
    self._build_command_call()

  @funnel
  def _run_cmd(self, cmd):
    """
    Use a semaphore to guarantee no race conditions, and cleanly
    resolve connection closure.
    """
    with DenonCommand(self.host, self.port) as session:
      session.send(cmd)
      return session.recieve()

  def _build_command_call(self):
    """
    Use _DenonCommandStore to build a command hierchy
    cmd_source -- denon api cmd dict
                  { category: name: [command, param] }
    """
    for parent in commands.available():
      for child in commands[parent]:
        child._call = self._register_cmd(child.cmd, child.params)
      setattr(self, parent, commands[parent])

  def _register_cmd(self, cmd_content, cmd_param=None):
    def _execute_cmd(*args):
      _cmd_param = cmd_param
      _cmd_content = cmd_content  
      if (_cmd_param is not None) and (len(args) == 0):
        sys.stderr.write('Missing parameter')
        return False
      elif cmd_param is not None:
        _param = commands.param_parser(args[0], _cmd_param)
        if _param:
          _cmd_content += '%s' % _param
          print(_cmd_content)
        else:
          sys.stderr.write('Invalid parameter: %s' % args[0])
          return False
      try:
        return self._run_cmd(_cmd_content)
      except DenonAvrConnectException as e:
        sys.stderr.write('Error: %s\n' % e)
    return _execute_cmd

  def __getitem__(self, key):
    if hasattr(self, key):
      return getattr(self, key)
    raise DenonAvrException('Invalid command: %s' % key)


class DenonCommand(object):

  """
  Run a single command.

  Example:
    with DenonCommand(<host>) as d:
      d.send(<command>)
      print(d.recieve())
  """

  def __init__(self, host, port, timeout=1.0, max_bytes=1024):
    self.host = host
    self.port = port
    self.timeout = timeout
    self.max_bytes = max_bytes

  def __enter__(self):
    try:
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.connect((self.host, self.port))
      self.reciever = _Reciever(self.sock, self.timeout, self.max_bytes)
      return self
    except Exception as e:
      raise DenonAvrConnectException('%s (%s:%s)' % (e[1], self.host, self.port))

  def __exit__(self, type, value, traceback):
    self.sock.close()
    if not isinstance(value, Exception):
      return True
    raise DenonAvrException(value)

  def send(self, content):
    self.sock.send(content + '\r')

  def recieve(self):
    return self.reciever.read()

  def recieve_string(self, *args, **kwargs):
    r = self.recieve(*args, **kwargs)
    return ''.join(r)


class _Reciever(object):

  """
  Internal class to handle data retrieval from a socket
  and guarantees a 'read' timeout.

  Arguments:
    socket -- instance of type socket
    timeout -- timeout in ms
    max_byates -- max data size to read
  """

  def __init__(self, socket, timeout, max_bytes):
    self.timeout = timeout
    self.process = _SocketReader(socket, max_bytes)
    self.process.daemon = True

  def read(self):
    t_start = time.time()
    self.process.start()
    _timeout = time.time() - t_start
    while (_timeout < self.timeout):
      if not self.process.is_alive():
        break
      self.block(milliseconds=10)
      """
      Note: timeout needs to be checked immediately after
      block releases, but before the next while-loop
      iteration
      """
      _timeout = time.time() - t_start
      if (_timeout >= self.timeout):
        break
    self.terminate()
    return self.process.get_data()

  def terminate(self):
    try:
      self.process.terminate()
    except Exception as e:
      pass

  def block(self, milliseconds):
    default = 10
    try:
      time.sleep(float(milliseconds) / 1000)
    except (TypeError, ValueError) as e:
      self.block(default)


class _SocketReader(Process):

  """
  A Process to incrementally read characters from a
  socket, where the return of data from the reader process
  can be retrieved from internal queue.

  Arguments:
    sock -- socket ready recv
    max_byates -- max message size in bytes
  """

  def __init__(self, sock, max_bytes):
    self._return_data = []
    self._ipc = queues.SimpleQueue()
    self._sock = sock
    self._max_bytes = max_bytes
    super(_SocketReader, self).__init__()

  def run(self):
    for byte in self._sock.recv(self._max_bytes):
      if byte in ('\r', '\n'):
        break
      self._return_data.append(codecs.encode(byte, 'utf8'))
    self._ipc.put(self._return_data)

  def get_data(self):
    if not self._ipc.empty():
      return self._ipc.get()
    return []


