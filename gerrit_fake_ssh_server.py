#!/usr/bin/env python
import inspect
import os
import select
import socket
import socketserver
import sys
import threading
import time
import traceback

import paramiko
from paramiko.py3compat import u

#PORT = 29418
PORT = 2200

host_key = paramiko.RSAKey(filename=os.path.join(os.path.dirname(__file__),
                                                 'gerrit-server-key'),
                           password='jenkins')

COMMANDS_MAP = {'gerrit version': '',
                'gerrit stream-events': '{}\r\n'}

GERRIT_CMD_VERSION = 'gerrit version 2.16.7\n'

GERRIT_SHELL_MSG = """
  ****    Welcome to Ferrit Code Review    ****\r
\r
  Hi Jenkins, you have successfully connected over SSH.\r
\r
  Unfortunately, interactive shells are disabled.\r
\r
"""


class Server(paramiko.ServerInterface):

    def __init__(self, client_address):
        self.event = threading.Event()
        self.client_address = client_address

    def check_channel_request(self, kind, chanid):
        print('Kind: %s, chanid: %s', kind, chanid)
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "password,publickey"

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_exec_request(self, channel, command):
        print("stack: %s", inspect.stack()[0][3])
        self.command = command
        self.event.set()
        return True

    def check_channel_shell_request(self, channel):
        print(inspect.stack()[0][3])
        self.command = None
        self.event.set()
        return True

    def check_channel_subsystem_request(self, channel, name):
        return True

    def check_channel_window_change_request(self, channel, width, height,
                                            pixelwidth, pixelheight):
        return True

    def check_channel_x11_request(self, channel, single_connection,
                                  auth_protocol, auth_cookie, screen_number):
        return True

    def check_channel_forward_agent_request(self, channel):
        return True

    def check_global_request(self, kind, msg):
        return True

    def check_channel_direct_tcpip_request(self, chanid, origin, destination):
        return True

    def check_channel_env_request(self, channel, name, value):
        print("channel: %s, name: %s, value: %s", channel, name, value)
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        return True


class SSHHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self._prev = None
        try:
            transport = paramiko.Transport(self.connection)
            transport.add_server_key(host_key)
            server = Server(self.client_address)
            try:
                transport.start_server(server=server)
            except paramiko.SSHException:
                return

            while True:
                print('powstaje kanał')

                # wait for auth
                channel = transport.accept(20)
                if channel is None:
                    transport.close()
                    return 1

                print('czekanie na coś')

                server.event.wait(10)
                if not server.event.is_set():
                    transport.close()
                    return 1

                print('coś przyszło!\n')

                __import__('pdb').set_trace()
                if server.command:
                    print('server_command %s' % server.command.decode('utf-8'))
                    print('%s' %
                          COMMANDS_MAP.get(server.command.decode('utf-8')))

                    cmd = server.command.decode('utf-8')

                    if cmd == 'gerrit version':
                        channel.send(GERRIT_CMD_VERSION)
                        channel.close()
                    elif cmd == 'gerrit stream-events':
                        while True:
                            time.sleep(1)
                    else:
                        channel.close()
                else:
                    __import__('pdb').set_trace()
                    channel.send_stderr(GERRIT_SHELL_MSG)
                    fobj = channel.makefile("rU")
                    fobj.read(1)
                    print(fobj.read(1))
                    print(fobj.read(1))
                    print(fobj.read(1))
                    while True:
                        r, w, e = select.select([channel, sys.stdin], [], [])
                        if channel in r:
                            try:
                                x = u(channel.recv(1024))
                                if len(x) == 0:
                                    sys.stdout.write("\r\n*** EOF\r\n")
                                    break
                                sys.stdout.write(x)
                                sys.stdout.flush()
                            except socket.timeout:
                                pass
                        if sys.stdin in r:
                            x = sys.stdin.read(1)
                            if len(x) == 0:
                                break
                            channel.send(x)

        except Exception as e:
            traceback.print_exc()
        finally:
            try:
                # channel.close()
                transport.close()
            except:
                pass


sshserver = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), SSHHandler)
sshserver.serve_forever()
