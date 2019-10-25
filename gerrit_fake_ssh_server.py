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
import logging

import paramiko
from paramiko.py3compat import u


PORT = 2200  # it could be even 29418, which is standard gerrit port

FILE_DIR = os.path.dirname(__file__)
BASE_NAME = os.path.extsep.join(os.path.basename(__file__)
                                .split(os.path.extsep)[:-1])
HOST_KEY = paramiko.RSAKey(filename=os.path.join(FILE_DIR,
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
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(FILE_DIR, BASE_NAME + '.log'))
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] '
                                       '%(filename)s:%(lineno)s - '
                                       '%(message)s'))
LOG.addHandler(handler)


class Server(paramiko.ServerInterface):

    def __init__(self, client_address):
        self.event = threading.Event()
        self.client_address = client_address

    def check_channel_request(self, kind, chanid):
        LOG.debug('Kind: %s, chanid: %s', kind, chanid)
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
        LOG.debug(inspect.stack()[0][3])
        self.command = command
        self.event.set()
        return True

    def check_channel_shell_request(self, channel):
        LOG.debug(inspect.stack()[0][3])
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
        LOG.debug("channel: %s, name: %s, value: %s", channel, name, value)
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        return True


class SSHHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self._prev = None
        try:
            transport = paramiko.Transport(self.connection)
            transport.add_server_key(HOST_KEY)
            server = Server(self.client_address)
            try:
                transport.start_server(server=server)
            except paramiko.SSHException:
                return

            while True:
                # wait for auth
                channel = transport.accept(20)
                if channel is None:
                    transport.close()
                    return 1

                server.event.wait(10)
                if not server.event.is_set():
                    transport.close()
                    return 1

                if server.command:
                    LOG.debug('server_command %s, mapped to: %s',
                              server.command.decode('utf-8'),
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
                    # interactive session
                    channel.send_stderr(GERRIT_SHELL_MSG)
                    return

        except Exception:
            traceback.print_exc()
        finally:
            transport.close()


def main():
    sshserver = socketserver.ThreadingTCPServer(('127.0.0.1', PORT),
                                                SSHHandler)
    sshserver.serve_forever()


if __name__ == "__main__":
    main()
