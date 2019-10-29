import logging
import os
import socketserver
import sys
import threading
import time
import traceback

import paramiko


# Those global variables meant to be set in parent module
FIFO = 'ferrit.fifo'
LOG_PATH = './'
KEY = './gerrit-server-key'

# it could be even 29418, which is standard gerrit port
PORT = 2200

GERRIT_CMD_PROJECTS = """All-Projects
All-Users
example
"""
GERRIT_CMD_VERSION = "ferrit version 0.0.1\n"
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
handler = logging.FileHandler(os.path.join(LOG_PATH, 'ferrit-ssh.log'))
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] '
                                       '%(filename)s:%(lineno)s %(funcName)s '
                                       '- %(message)s'))
LOG.addHandler(handler)


class Server(paramiko.ServerInterface):
    def __init__(self, client_address):
        LOG.debug('client_address: %s', client_address)
        self.command = None
        self.event = threading.Event()
        self.client_address = client_address

    def check_channel_request(self, kind, chanid):
        LOG.debug('kind: %s, chanid: %s', kind, chanid)
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        LOG.debug('username: %s', username)
        return "password,publickey"

    def check_auth_password(self, username, password):
        LOG.debug('username: %s, password: %s', username, password)
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        LOG.debug('username: %s, key: %s', username, str(key)[:11])
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_exec_request(self, channel, command):
        LOG.debug('channel: %s, command: %s', channel.get_id(), command)
        self.command = command
        self.event.set()
        return True

    def check_channel_shell_request(self, channel):
        LOG.debug('channel: %s', channel.get_id())
        self.event.set()
        return True

    def check_global_request(self, kind, msg):
        LOG.debug('kind: %s, msg: %s', kind, msg.get_text())
        return True

    def check_channel_env_request(self, channel, name, value):
        LOG.debug("channel: %s, name: %s, value: %s",
                  channel.get_id(), name, value)
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
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
                        with open(FIFO) as fobj:
                            data = fobj.read()
                        if not data:
                            time.sleep(1)
                        else:
                            LOG.debug("Writing %s to channel", data)
                            channel.send(data)
                            data = None

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
    os.mkfifo(FIFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] '
                                           '%(funcName)s:%(lineno)s - '
                                           '%(message)s'))
    LOG.addHandler(handler)
    LOG.debug('Start up development server')
    try:
        main()
    finally:
        os.unlink(FIFO)
