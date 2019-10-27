import bottle


@bottle.route('/plugins/events-log/')
def events_log(params=None):
    return ''


@bottle.route('/a/projects/')
def projects(params=None):
    """
    Possible params (accessible via bottle.request.params) is 'd'
    """
    return {"All-Projects": {"id": "All-Projects",
                             "description": "all projects",
                             "state": "ACTIVE",
                             "web_links": [{"name": "browse",
                                            "url":
                                            "/plugins/gitiles/All-Projects",
                                            "target": "_blank"}]},
            "All-Users": {"id": "All-Users",
                          "description": "users",
                          "state": "ACTIVE",
                          "web_links": [{"name": "browse",
                                         "url": "/plugins/gitiles/All-Users",
                                         "target": "_blank"}]},
            "DEDICATED": {"id": "DEDICATED",
                          "state": "ACTIVE",
                          "web_links": [{"name": "browse",
                                         "url": "/plugins/gitiles/DEDICATED",
                                         "target": "_blank"}]}}


@bottle.post('/a/changes/<project>~<branch>~<id>/revisions/<commit_id>/review')
def changes(project, branch, id, commit_id):
    # We are looking for labels in the json
    labels = bottle.request.json.get('labels', {})
    if not labels:
        return

    # TODO(gryf): It's on gerrit side now. What we do with this information on
    # Ferrit? Verified is either 1 or -1, which indicates build in jenkins
    if labels.get('Verified') == 1:
        return True
    else:
        return False


@bottle.route('/a/plugins/events-log/events/')
def events(t1=None):
    return {}


bottle.run(host='localhost', port=8181, debug=True)
