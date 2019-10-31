import json
import os
import signal
import subprocess
import time
import unittest

import requests


class TestPatchCreate(unittest.TestCase):
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
        time.sleep(5)  # give some time to processes to start

    def tearDown(self):
        os.killpg(self.process.pid, signal.SIGTERM)
        os.unlink('ferrit-http.log')
        os.unlink('ferrit-ssh.log')

    def test_send_patch(self):
        counter = 15
        result = []
        pipe = subprocess.Popen('ssh -i gerrit-access-key localhost -p 2200 '
                                'gerrit stream-events'.split())
        time.sleep(3)
        requests.post('http://localhost:8181/make/event', data='project='
                      'example&branch=master&type=patchset-created')
        while counter:
            if not os.path.exists('ferrit-http.log'):
                counter -= 1
                time.sleep(1)
                continue

            with open('ferrit-http.log') as fobj:
                result = fobj.read()
                if not result:
                    time.sleep(1)
                    counter -= 1
                else:
                    break

        pipe.terminate()

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(result['labels']['Verified'], 1)
