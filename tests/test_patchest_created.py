import json

from tests import base


class TestPatchsetCreated(base.BaseTestCase):

    def test_send_patch(self):
        result = self._send_and_get_response('patchset-created')

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(result['labels']['Verified'], 1)
