#!/usr/bin/env python

from binascii import hexlify
import os
import socket
import sys
import threading
import traceback
import socketserver
import logging
import time
import inspect
import select
#import random

import paramiko
from paramiko.py3compat import b, u

PORT = 2200
LOG_FILE = 'fakessh.log'


host_key = paramiko.RSAKey(filename='gerrit-server-key', password='jenkins')

COMMANDS_MAP = {'gerrit version': '',
                'gerrit stream-events': '{}\r\n'}

GERRIT_CMD_VERSION = 'gerrit version 2.16.7\n'

GERRIT_SHELL_MSG = '''\r
  ****    Welcome to Gerrit Code Review    ****\r
\r
  Hi Jenkins, you have successfully connected over SSH.\r
\r
  Unfortunately, interactive shells are disabled.\r
  To clone a hosted Git repository, use:\r
\r
  git clone ssh://jenkins@review.dev.cloud.company.net:29418/REPOSITORY_NAME.git\r
\r
'''


class Server(paramiko.ServerInterface):

    def __init__(self, client_address):
        self.event = threading.Event()
        self.client_address = client_address

    def check_channel_request(self, kind, chanid):
        print(kind, chanid)
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
        print(inspect.stack()[0][3])
        self.command = command
        self.event.set()
        return True

    def check_channel_shell_request(self, channel):
        print(inspect.stack()[0][3])
        self.command = None
        self.event.set()
        return True

    def check_channel_subsystem_request(self, channel, name):
        print(inspect.stack()[0][3])
        return True
    def check_channel_window_change_request(self, channel, width, height, pixelwidth, pixelheight):
        print(inspect.stack()[0][3])
        return True
    def check_channel_x11_request(self, channel, single_connection, auth_protocol, auth_cookie, screen_number):
        print(inspect.stack()[0][3])
        return True
    def check_channel_forward_agent_request(self, channel):
        print(inspect.stack()[0][3])
        return True
    def check_global_request(self, kind, msg):
        print(inspect.stack()[0][3])
        return True
    def check_channel_direct_tcpip_request(self, chanid, origin, destination):
        print(inspect.stack()[0][3])
        return True
    def check_channel_env_request(self, channel, name, value):
        print(inspect.stack()[0][3])
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        print(inspect.stack()[0][3])
        return True


class SSHHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self._prev = None
        try:
            t = paramiko.Transport(self.connection)
            t.add_server_key(host_key)
            server = Server(self.client_address)
            try:
                t.start_server(server=server)
            except paramiko.SSHException:
                return

            while True:
                print('powstaje kanał')

                # wait for auth
                chan = t.accept(20)
                if chan is None:
                    t.close()
                    return 1

                print('czekanie na coś')

            #import pdb; pdb.set_trace()

                server.event.wait(10)
                if not server.event.is_set():
                    t.close()
                    return 1

                # import pdb; pdb.set_trace()
                print('coś przyszło!\n')

                #import pdb; pdb.set_trace()            

                if server.command:
                    print('Jest komenda! {}'.format(server.command))
                    print('server_command %s' % server.command.decode('utf-8'))
                    print('%s' % COMMANDS_MAP.get(server.command.decode('utf-8')))
                    #chan.send(COMMANDS_MAP.get(server.command.decode('utf-8'),  '{}\r'))
                    #chan.close()

                    cmd = server.command.decode('utf-8')

                    if cmd == 'gerrit version':
                        chan.send(GERRIT_CMD_VERSION)
                        chan.close()
                    elif cmd == 'gerrit stream-events':
                        while True:
                            time.sleep(1)
                    else:
                        chan.close()
                else:
                    chan.send_stderr(GERRIT_SHELL_MSG)
                    f = chan.makefile("rU")
                    f.read(1)
                    print(f.read(1))
                    print(f.read(1))
                    print(f.read(1))
                    while True:
                        r, w, e = select.select([chan, sys.stdin], [], [])
                        if chan in r:
                            try:
                                x = u(chan.recv(1024))
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
                            chan.send(x)


        except Exception as e:
            traceback.print_exc()
        finally:
            try:
                t.close()
            except:
                pass


sshserver = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), SSHHandler)
sshserver.serve_forever()



