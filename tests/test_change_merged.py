import json

from tests import base


class TestChangeMerged(base.BaseTestCase):

    def test_deploy(self):
        result = self._send_and_get_response('change-merged')

        self.assertTrue(result)
        result = json.loads(result)
        self.assertIn('--tag', result['message'])
