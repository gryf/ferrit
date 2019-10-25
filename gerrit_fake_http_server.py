import bottle


@bottle.route('/plugins/events-log/')
def events(params=None):
    return """
)]}'
{
  "name": "plugins/events-log",
  "clone_url": "http://localhost:8181/plugins/events-log",
  "description": "This plugin listens to stream events and stores them in a database. The events can be retrieved through REST API."
}"""


@bottle.route('/a/projects/')
def projects(params=None):
    """
    Possible params (accessible via bottle.request.params) is 'd'
    """
    print(params)
    return {
  "All-Projects": {
    "id": "All-Projects",
    "description": "Rights inherited by all other projects.",
    "state": "ACTIVE",
    "web_links": [
      {
        "name": "browse",
        "url": "/plugins/gitiles/All-Projects",
        "target": "_blank"
      }
    ]
  },
  "All-Users": {
    "id": "All-Users",
    "description": "Individual user settings and preferences.",
    "state": "ACTIVE",
    "web_links": [
      {
        "name": "browse",
        "url": "/plugins/gitiles/All-Users",
        "target": "_blank"
      }
    ]
  },
  "DEDICATED": {
    "id": "DEDICATED",
    "state": "ACTIVE",
    "web_links": [
      {
        "name": "browse",
        "url": "/plugins/gitiles/DEDICATED",
        "target": "_blank"
      }
    ]
  },
  "DEDICATED/ironic": {
    "id": "DEDICATED%2Fironic",
    "state": "ACTIVE",
    "web_links": [
      {
        "name": "browse",
        "url": "/plugins/gitiles/DEDICATED/ironic",
        "target": "_blank"
      }
    ]
  }
}

bottle.run(host='localhost', port=8181, debug=True)
