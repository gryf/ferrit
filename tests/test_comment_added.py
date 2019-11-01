import json

from tests import base


class TestCommentAdded(base.BaseTestCase):

    def test_recheck(self):
        result = self._send_and_get_response('comment-added')

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(result['labels']['Verified'], 1)
