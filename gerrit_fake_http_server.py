import bottle


@bottle.route('/plugins/events-log/')
def events(params=None):
    return bottle.redirect('/plugins/events-log/Documentation/index.html', code=302)

@bottle.route('/plugins/events-log/Documentation/index.html')
def events(params=None):
     return """
<html><head><title>Plugin events-log</title></head><body>
<h1 id="plugin-events-log">Plugin events-log</h1>
<table class="plugin_info"><tr><th>Name</th><td>events-log plugin</td></tr>
<tr><th>Version</th><td>v2.13-178-g68fcb6a4b1</td></tr>
</table>
<h2><a href="#about" id="about">About</a></h2>
<p>This plugin listens to stream events and stores them in a database. The events can be retrieved through REST API. Some use cases for this plugin include debugging for admins; also users who use scripts which listen to stream events can query for any events that they might have missed.</p>
<h2><a href="#documentation" id="documentation">Documentation</a></h2>
<ul>
<li><a href="build.md">Build</a></li>
<li><a href="config.md">events-log Configuration</a></li>
</ul>
<h2><a href="#rest-apis" id="rest-apis">REST APIs</a></h2>
<ul>
<li><a href="rest-api-events.md">events-log - /events/ REST API</a></li>
</ul>
</body></html>
"""

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
