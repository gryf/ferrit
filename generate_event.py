#!/usr/bin/env python

import argparse
import json
import sys
import time


TEMPLATES = {'patchset-created':
             {"change": {"branch": "master",
                         "commitMessage": "commit msg",
                         "id": "I4558cc1a87488d4a385972c71c048c808cc6e1ef",
                         "number": "691277",
                         "owner": {"email": "j.doe@nonexistent.com",
                                   "name": "John Doe",
                                   "username": "jdoe"},
                         "project": "foo",
                         "status": "NEW",
                         "subject": "create new patch",
                         "url": "http://localhost:8181/1"},
              "changeKey": {"id": "I4558cc1a87488d4a385972c71c048c808cc6e1ef"},
              "eventCreatedOn": int(time.time()),
              "patchSet": {"author": {"email": "j.doe@nonexistent.com",
                                      "name": "John Doe",
                                      "username": "jdoe"},
                           "createdOn": int(time.time()) - 1000,
                           "isDraft": False,
                           "kind": "REWORK",
                           "number": "1",
                           "parents": ["559721d9"],
                           "ref": "refs/changes/77/691277/1",
                           "revision": "e3c8ac50",
                           "sizeDeletions": -15,
                           "sizeInsertions": 29,
                           "uploader": {"email": "j.doe@nonexistent.com",
                                        "name": "John Doe",
                                        "username": "jdoe"}},
              "project": "foo",
              "refName": "refs/heads/master",
              "type": "patchset-created",
              "uploader": {"email": "j.doe@nonexistent.com",
                           "name": "John Doe",
                           "username": "jdoe"}}}


def generate(args):
    template = TEMPLATES[args.type]
    json.dump(template, sys.stdout)
    sys.stdout.write('\n')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('type', choices=TEMPLATES.keys())
    args = parser.parse_args()
    generate(args)


if __name__ == "__main__":
    main()
