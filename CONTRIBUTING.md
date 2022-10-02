Development guide
=================

Requirements
------------

Install and configure :

* docker
* molecule
* molecule-docker

Run tests
---------

```sh
molecule test
```

Develop / Debug
---------------

```sh
molecule create
molecule converge
molecule login -h <instance_name>
# Do your changes by hand
molecule verify
```

Submit your changes
-------------------

Merge request in Gitlab.
