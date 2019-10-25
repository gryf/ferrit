#!/usr/bin/env python
import inspect
import logging
import os
import socketserver
import sys
import threading
import time
import traceback

import paramiko


# it could be even 29418, which is standard gerrit port
PORT = 2200

FILE_DIR = os.path.dirname(__file__)
BASE_NAME = os.path.extsep.join(os.path.basename(__file__)
                                .split(os.path.extsep)[:-1])
HOST_KEY = paramiko.RSAKey(filename=os.path.join(FILE_DIR,
                                                 'gerrit-server-key'),
                           password='jenkins')

GERRIT_CMD_PROJECTS = """All-Projects
All-Users
openstack
openstack/nova
openstack/neutron
"""
GERRIT_CMD_VERSION = "ferrit version 2.16.7\n"
GERRIT_SHELL_MSG = """\r
  ****    Welcome to Ferrit Code Review    ****\r
\r
  Hi Jenkins, you have successfully connected over SSH.\r
\r
  Unfortunately, interactive shells are disabled.\r
  To clone a hosted Git repository, use:\r
\r
  git clone ssh://localhost:{GERRIT_PORT}/REPOSITORY_NAME.git\r
\r
""".format(GERRIT_PORT=PORT)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(FILE_DIR, BASE_NAME + '.log'))
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] '
                                       '%(filename)s:%(lineno)s - '
                                       '%(message)s'))
LOG.addHandler(handler)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] '
                                       '%(filename)s:%(lineno)s - '
                                       '%(message)s'))
LOG.addHandler(handler)


class Server(paramiko.ServerInterface):
    def __init__(self, client_address):
        LOG.debug('%s', inspect.stack()[0][3])
        LOG.debug('client_address: %s', client_address)
        self.command = None
        self.event = threading.Event()
        self.client_address = client_address

    def check_channel_request(self, kind, chanid):
        LOG.debug('%s', inspect.stack()[0][3])
        LOG.debug('kind: %s, chanid: %s', kind, chanid)
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        LOG.debug('%s', inspect.stack()[0][3])
        LOG.debug('username: %s', username)
        return "password,publickey"

    def check_auth_password(self, username, password):
        LOG.debug('%s', inspect.stack()[0][3])
        LOG.debug('username: %s, password: %s', username, password)
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        LOG.debug('%s', inspect.stack()[0][3])
        LOG.debug('username: %s, key: %s', username, str(key)[:11])
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_exec_request(self, channel, command):
        LOG.debug('%s', inspect.stack()[0][3])
        LOG.debug('channel: %s, command: %s', channel.get_id(), command)
        self.command = command
        self.event.set()
        return True

    def check_channel_shell_request(self, channel):
        LOG.debug('%s', inspect.stack()[0][3])
        LOG.debug('channel: %s', channel.get_id())
        self.event.set()
        return True

    def check_global_request(self, kind, msg):
        LOG.debug('%s', inspect.stack()[0][3])
        LOG.debug('kind: %s, msg: %s', kind, str(msg))
        return True

    def check_channel_env_request(self, channel, name, value):
        LOG.debug('%s', inspect.stack()[0][3])
        LOG.debug("channel: %s, name: %s, value: %s",
                  channel.get_id(), name, value)
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        LOG.debug('%s', inspect.stack()[0][3])
        LOG.debug("channel: %s, term: %s, width: %s, height: %s, "
                  "pixelwidth: %s, pixelheight: %s, modes: %s",
                  channel.get_id(), term, width, height,
                  pixelwidth, pixelheight, str(modes)[:7])
        return True


class SSHHandler(socketserver.StreamRequestHandler):
    def handle(self):
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
                    cmd = server.command.decode('utf-8')
                    LOG.debug('received server command: %s', cmd)

                    if cmd == 'gerrit version':
                        LOG.debug('sending version string')
                        channel.send(GERRIT_CMD_VERSION)
                        channel.close()

                    elif cmd == 'gerrit ls-projects':
                        LOG.debug('sending list of projects')
                        channel.send(GERRIT_CMD_PROJECTS)
                        channel.close()

                    elif cmd == 'gerrit stream-events':
                        LOG.debug('sending events from queue...')
                        while True:
                            time.sleep(1)
                            pass # TODO: implement queue or something here

                    else:
                        LOG.debug('unknown command -- closing channel')
                        channel.close()

                else:
                    LOG.debug('requested interactive session')
                    channel.send_stderr(GERRIT_SHELL_MSG)
                    channel.makefile("rU").read(1)  # wait for any key press
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
