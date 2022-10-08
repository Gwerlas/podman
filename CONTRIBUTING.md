Development guide
=================

This role should not need any external settings to work.

Requirements
------------

Install and configure :

* docker
* molecule
* molecule-docker

Supporting a new distribution / version
---------------------------------------

To add support to a new distribution / version, You can define some defaults if its
packages does not work out of the box.

Use the files in the `vars` directory to do it. You can use the dictionaries below :

- `podman_containers_defaults`
- `podman_registries_defaults`
- `podman_storage_defaults`

The users `podman_*_config` will be merged with the respective `podman_*_defaults`.

Use this facility only if the distribution packages does not work out of the box.

Look at the `vars/debian11.yml` for example.

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
