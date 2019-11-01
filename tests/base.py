import os
import signal
import subprocess
import time
import unittest


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        if not all((os.path.exists('gerrit-server-key'),
                    os.path.exists('gerrit-access-key'))):
            raise SystemError("No server key-pair or access key-pair found. "
                              "You'll need to copy them to the current "
                              "directory under name 'gerrit-server-key' and "
                              "'gerrit-server-key.pub' for server keyes and "
                              "'gerrit-access-key' and "
                              "'gerrit-access-key.pub' for access keyes. "
                              "Don't forget to run configured Jenkins!")
        self.process = subprocess.Popen(['ferrit'], preexec_fn=os.setpgrp)
        # give some time for processes to start, and jenkins to be ready for
        # consume the data
        time.sleep(3)

    def tearDown(self):
        os.killpg(self.process.pid, signal.SIGTERM)
        os.unlink('ferrit-http.log')
        os.unlink('ferrit-ssh.log')
