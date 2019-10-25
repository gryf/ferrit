import bottle


@bottle.route('/plugins/events-log/')
def events(params=None):
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


bottle.run(host='localhost', port=8181, debug=True)
