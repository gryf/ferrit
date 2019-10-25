======
Ferrit
======

.. image:: img/ferrit.jpg
   :alt: Ferrit


Ferrit is a fake Gerrit server implementation created for functional testing of
events in Jenkins & Gerrit Trigger ecosystem.

----

Architecture
------------

Ferrit consists of two servers, http and ssh and companion script for
generating payload for the ssh server.

We relay on real Jenkins installation, so it has to be configured up front. See
next section for details.

Having Jenkins up and running, we can simultaneously run ssh and http servers
by invoking:

.. code:: shell-session

   $ python3 gerrit_fake_http_server.py

and

.. code:: shell-session

   $ python3 gerrit_fake_ssh_server.py

Output of the last command will provide fifo file name used for triggering
events in json format which can be generated using third part of the Ferrit -
script `generate_event.py`.

Installation
------------

Prerequisites
=============

.. TODO (jenkins, plugins installation and configuration)



Python
======

Ferrit modules are written in Python and depends on two external libraries:

- `paramiko`_ for ssh server
- `bottle`_ for http server

Please note, Python 2.x is not supported.


`Ferrite image`_ by Karl-Martin Skontorp is on Attribution 2.0 Generic (CC BY
2.0) license.

.. _Ferrite image: https://www.flickr.com/photos/picofarad-org/2132206570/
.. _paramiko: https://www.paramiko.org/
.. _bottle: https://bottlepy.org
