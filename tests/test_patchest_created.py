import json
import os
import time

import requests

from tests import base


class TestPatchsetCreated(base.BaseTestCase):

    def test_send_patch(self):
        counter = 20
        result = None
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

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(result['labels']['Verified'], 1)
