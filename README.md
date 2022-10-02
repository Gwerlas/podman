Podman
======

[![pipeline status](https://gitlab.com/yoanncolin/ansible/roles/podman/badges/main/pipeline.svg)](https://gitlab.com/yoanncolin/ansible/roles/podman/-/commits/main)

Install and configure podman in rootless mode.

GitLab project : [yoanncolin/ansible/roles/podman](https://gitlab.com/yoanncolin/ansible/roles/podman)

Requirements
------------

The Linux base system configured with :

- SSH
- Python (for Ansible)
- Sudo
- Package manager ready to use

The `gwerlas.system` role can help You :

```sh
ansible-galaxy install gwerlas.system
```

```yaml
- name: My playbook
  hosts: all
  roles:
    - gwerlas.system
    - gwerlas.podman
```

Role Variables
--------------

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
podman_compose_install: false
podman_toolbox_install: false

podman_mimic_docker: false

podman_users:
  - "{{ ansible_user_id }}"
```

### Podman compose

The `podman_compose_install` set to `true` will install `podman-compose` if it is available
for the distribution of the targetted host.

### Podman toolbox

The `podman_toolbox_install` set to `true` will install `podman-toolbox` if it is available
for the distribution of the targetted host.

### Mimic Docker

#### Docker in the $PATH

You can mimic Docker throw the `podman_mimic_docker` parameter set to `true`. If the package
`podman-docker` is available for the target Linux distribution, il will be installed, or a
symlink will be created either.

So the scripts calling `docker` will transparently use `podman` instead.

#### Daemon socket

If the installed version of Podman is `3.0` or upper, the service will be started and
enabled and the environment variables `DOCKER_BUILDKIT` and `DOCKER_HOST` will be respectively set to `0`
and `$XDG_RUNTIME_DIR/podman/podman.sock`.

So you will be able to reach podman throw the Unix socket or the network like Docker does.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

Facts
-----

After the podman installation, the `podman_current_version` fact is set to permit
some checks, and to adapt the code for the target node.

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
