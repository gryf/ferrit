import logging
import os

import bottle


# This global variable meant to be set in module, which imports this one
FIFO = None
FILE_DIR = os.path.dirname(__file__)
BASE_NAME = os.path.extsep.join(os.path.basename(__file__)
                                .split(os.path.extsep)[:-1])
LOG = logging.getLogger('bottle')
LOG.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(FILE_DIR, BASE_NAME + '.log'))
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] '
                                       '%(filename)s:%(lineno)s - '
                                       '%(message)s'))
LOG.addHandler(handler)


class App(bottle.Bottle):
    def __init__(self):
        super(App, self).__init__()
        self.route('/Documentation/<whatever>', callback=self._documentation)
        self.route('/plugins/events-log/', callback=self._events_log)
        self.route('/plugins/events-log/events/', callback=self._events)
        self.route('/a/projects/', callback=self._projects)
        self.post('/a/changes/<project>~<branch>~<id>/revisions/<commit_id>'
                  '/review', callback=self._changes)

    def _documentation(self, whatever, params=None):
        return ''

    def _events_log(params=None):
        return ''

    def _events(self, t1=None):
        return {}

    def _projects(params=None):
        """
        Possible params (accessible via bottle.request.params) is 'd'
        """
        return {"All-Projects": {"id": "All-Projects",
                                 "description": "all projects",
                                 "state": "ACTIVE",
                                 "web_links": [{"name": "browse",
                                                "url":
                                                "/plugins/gitiles/All-"
                                                "Projects",
                                                "target": "_blank"}]},
                "All-Users": {"id": "All-Users",
                              "description": "users",
                              "state": "ACTIVE",
                              "web_links": [{"name": "browse",
                                             "url": "/plugins/gitiles/"
                                             "All-Users",
                                             "target": "_blank"}]},
                "example": {"id": "example",
                            "description": "example ptoject",
                            "state": "ACTIVE",
                            "web_links": [{"name": "browse",
                                           "url": "/plugins/gitiles/example",
                                           "target": "_blank"}]}}

    def _changes(self, project, branch, id, commit_id):
        # We are looking for labels in the json
        labels = bottle.request.json.get('labels', {})
        if not labels:
            return

        if labels.get('Verified') == 1:
            LOG.info('True')
        else:
            LOG.info('False')


def main():
    app = App()
    app.run(port=8181, host='localhost', debug=False, quiet=True)


if __name__ == "__main__":
    # development version, meant to be run as stand alone module, like
    # python -m ferrit.http
    app = App()
    app.run(port=8181, host='localhost', debug=True, reloader=True)
