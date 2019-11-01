import json
import logging
import os
import sys
import time

import bottle


# This global variable meant to be set in module, which imports this one
FIFO = 'ferrit.fifo'
LOG_PATH = './'

LOG = logging.getLogger('bottle')
LOG.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(LOG_PATH, 'ferrit-http.log'))
handler.setFormatter(logging.Formatter('%(message)s'))
LOG.addHandler(handler)

JDOE = {"email": "j.doe@nonexistent.com",
        "name": "John Doe",
        "username": "jdoe"}
PATCHSET_CREATED = {"change": {"branch": "master",
                               "commitMessage": "commit msg",
                               "id": "I1",
                               "number": "1",
                               "owner": JDOE,
                               "project": "example",
                               "status": "NEW",
                               "subject": "create new patch",
                               "url": "http://localhost:8181/1"},
                    "changeKey": {"id": "I1"},
                    "eventCreatedOn": int(time.time()),
                    "patchSet": {"author": JDOE,
                                 "createdOn": int(time.time()) - 1000,
                                 "isDraft": False,
                                 "kind": "REWORK",
                                 "number": "1",
                                 "parents": ["2"],
                                 "ref": "refs/changes/77/1/1",
                                 "revision": "e3c8ac50",
                                 "sizeDeletions": -15,
                                 "sizeInsertions": 29,
                                 "uploader": JDOE},
                    "project": "example",
                    "refName": "refs/heads/master",
                    "type": "patchset-created",
                    "uploader": JDOE}
RECHECK = {"approvals": [{"description": "Verified",
                          "type": "Verified",
                          "value": "0"},
                         {"description": "Code-Review",
                          "type": "Code-Review",
                          "value": "0"},
                         {"description": "Workflow",
                          "type": "Workflow",
                          "value": "0"}],
           "author": JDOE,
           "change": {"branch": "master",
                      "commitMessage": "commit msg",
                      "id": "I1",
                      "number": "690077",
                      "owner": JDOE,
                      "project": "example",
                      "status": "NEW",
                      "subject": "create new patch",
                      "topic": "test",
                      "url": "http://localhost:8181/1"},
           "changeKey": {"id": "I1"},
           "comment": "Patch Set 1:\n\nrecheck",
           "eventCreatedOn": int(time.time()),
           "patchSet": {"author": JDOE,
                        "createdOn": int(time.time()) - 1000,
                        "isDraft": False,
                        "kind": "NO_CODE_CHANGE",
                        "number": "1",
                        "parents": ["2"],
                        "ref": "refs/changes/77/1/1",
                        "revision": "e3c8ac50",
                        "sizeDeletions": -15,
                        "sizeInsertions": 29,
                        "uploader": JDOE},
           "project": "example",
           "refName": "refs/heads/master",
           "type": "comment-added"}
MERGED = {"change": {"branch": "master",
                     "commitMessage": "commit msg",
                     "id": "I1",
                     "number": "1",
                     "owner": JDOE,
                     "project": "example",
                     "status": "MERGED",
                     "subject": "create new patch",
                     "topic": "test",
                     "url": "http://localhost:8181/3"},
          "changeKey": {"id": "I1"},
          "eventCreatedOn": int(time.time()),
          "newRev": "0ce5beac",
          "patchSet": {
                       "author": JDOE,
                       "createdOn": int(time.time()) - 1000,
                       "isDraft": False,
                       "kind": "REWORK",
                       "number": "3",
                       "parents": ["1"],
                       "ref": "refs/changes/77/1/1",
                       "revision": "e3c8ac50",
                       "sizeDeletions": -8,
                       "sizeInsertions": 83,
                       "uploader": JDOE},
          "project": "example",
          "refName": "refs/heads/master",
          "submitter": {"name": "CI",
                        "username": "ci"},
          "type": "change-merged"}


class App(bottle.Bottle):
    def __init__(self):
        super(App, self).__init__()
        self.route('/Documentation/<whatever>', callback=self._documentation)
        self.route('/plugins/events-log/', callback=self._events_log)
        self.route('/a/plugins/events-log/events/', callback=self._events)
        self.route('/a/projects/', callback=self._projects)
        self.post('/a/changes/<project>~<branch>~<id>/revisions/<commit_id>'
                  '/review', callback=self._changes)
        self.post('/make/event', callback=self._mk_event)

    def _mk_event(self):
        events = {PATCHSET_CREATED['type']: PATCHSET_CREATED,
                  RECHECK['type']: RECHECK,
                  MERGED['type']: MERGED}

        if bottle.request.forms.get('type') not in events.keys():
            return

        data = dict(events[bottle.request.forms.get('type')])
        if 'project' in bottle.request.forms:
            data['change']['project'] = bottle.request.forms['project']
            data['project'] = bottle.request.forms['project']

        if 'branch' in bottle.request.forms:
            data['change']['branch'] = bottle.request.forms['branch']

        with open(FIFO, 'w') as fobj:
            fobj.write(json.dumps(data))
            fobj.write('\n')

    def _documentation(self, whatever, params=None):
        return

    def _events_log(self, params=None):
        return

    def _events(self):
        return

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

        LOG.info(json.dumps(bottle.request.json))


def main():
    app = App()
    app.run(port=8181, host='localhost', debug=False, quiet=True)


if __name__ == "__main__":
    # development version, meant to be run as stand alone module, like
    # python -m ferrit.rest
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    LOG.addHandler(handler)

    app = App()
    app.run(port=8181, host='localhost', debug=True)
