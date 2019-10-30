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

Ferrit consists of two servers, http and ssh.

We relay on real Jenkins installation, so it has to be configured up front. See
next section for details.

Having Jenkins up and running, we can simultaneously run ssh and http servers
by invoking:

.. code:: shell-session

   $ ferrit

To trigger the build initiated by gerrit fake server, use the curl utility to
send appropriate data to jenkins server:

.. code:: shell-session

   $ curl -d 'project=example&branch=master&type=patchset-created' \
     http://localhost:8181/make/event

With this command, we tell ferrit http server, to prepare right payload with
project set to *example*, branch set to *master* and type of the event to
*patchset-created*. This will build a json-like structure and send it through
the fifo queue to the SSH server, which will be catch by jenkins, who is
listing to the events. If the project and branch match, appropriate job will be
executed.


Installation
------------

Prerequisites
=============

.. TODO (jenkins, plugins installation and configuration)

SSH keys
========

For both - jenkins and ferrit server, you'll need ssh key. To generate it for
paramiko is a bit tricky, depending which version of openssh you have
installed.

For versions prior to 7.8, it is enough to issue a command:

.. code:: shell-session

   $ ssh-keygen -f gerrit-server-key

but for 7.8 and up:

.. code:: shell-session

   $ ssh-keygen -f gerrit-server-key -m pem

Python
======

Ferrit modules are written in Python and depends on two external libraries:

- `paramiko`_ for ssh server
- `bottle`_ for http server

Installation is as easy as issuing command:

.. code:: shell-session

   $ pip install .

in root of this repository. You can use virtualenv for your convenience. All
dependencies will be installed automatically.

Please note, Python 2.x is not supported.

----

`Ferrite image`_ by Karl-Martin Skontorp is on Attribution 2.0 Generic (CC BY
2.0) license.

.. _Ferrite image: https://www.flickr.com/photos/picofarad-org/2132206570/
.. _paramiko: https://www.paramiko.org/
.. _bottle: https://bottlepy.org
