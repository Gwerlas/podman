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

podman_wrappers: []
podman_wrappers_path: /usr/local/bin
```

### Podman configuration

By default, we let the configuration files of the distribution inchanged.

Except for the Debian 11 containers settings who does not work out of the box.

To use a customized configuration, use `podman_*_config` settings.

#### Containers

Use the `podman_containers_config` dictionary to populate the `/etc/containers/containers.conf`
file following the same structure as the toml described in [`containers.conf`][] man page.

[`containers.conf`]: https://man.archlinux.org/man/containers.conf.5.en

For example :

```yaml
podman_containers_config:
  containers:
    log_driver: journald
  engine:
    cgroup_manager: cgroupfs
```

Will generate the `/etc/containers/containers.conf` bellow :

```ini
[containers]
log_drivers = "journald"

[engine]
cgroup_manager = "cgroupfs"
```

For Debian 11 only, we overwrite the distribution defaults by the configuration above.

#### Registries

**NOTE** We do not support the deprecated version 1 format.

Use the `podman_registries_config` dictionary to populate the `/etc/containers/registries.conf`
file following the same structure as the toml described in [`registries.conf`][] man page.

[`registries.conf`]: https://man.archlinux.org/man/containers-registries.conf.5

For example :

```yaml
podman_registries_config:
  unqualified-search-registries:
    - docker.io
  registry:
    - location: my-insecure-registry:5000
      insecure: true
```

Will generate the `/etc/containers/registries.conf` bellow :

```ini
unqualified-search-registries = ['docker.io']

[[registry]]
location = my-insecure-registry:5000
insecure = true
```

#### Storage

Use the `podman_storage_config` dictionary to populate the `/etc/containers/storage.conf`
file following the same structure as the toml described in [`storage.conf`][] man page.

[`storage.conf`]: https://github.com/containers/storage/blob/main/docs/containers-storage.conf.5.md

For example :

```yaml
podman_storage_config:
  storage:
    driver: zfs
    options:
      zfs:
        mountopt: "nodev"
```

Will generate the `/etc/containers/storage.conf` bellow :

```ini
[storage]
driver = "zfs"

[storage.options.zfs]
mountopt = "nodev"
```
#### Libpod

Use the `podman_libpod_config` dictionary to populate the `/etc/containers/libpod.conf`
file following the same structure as the toml described in [`libpod.conf`][] man page.

[`libpod.conf`]: https://manpages.debian.org/unstable/podman/libpod.conf.5.en.html

For example :

```yaml
podman_libpod_config:
  cgroup_manager: cgroupfs
```

Will generate the `/etc/containers/libpod.conf` bellow :

```ini
cgroup_manager = "cgroupfs"
```

For Debian 11 only, we overwrite the distribution defaults by the configuration above.

### Podman compose

The `podman_compose_install` set to `true` will install `podman-compose` if it is available
for the distribution of the targetted host.

### Podman toolbox

The `podman_toolbox_install` set to `true` will install `podman-toolbox` if it is available
for the distribution of the targetted host.

### Mimic Docker

#### Docker in the $PATH

You can mimic Docker throw the `podman_mimic_docker` parameter set to `true`. If the package
`podman-docker` is available for the target Linux distribution, il will be installed, in the
other cases a symlink will be created.

So the scripts calling `docker` will transparently use `podman` instead, or almost.

#### Daemon socket

If the installed version of Podman is `3.0` or upper, the service will be enabled for each
`podman_users` and the environment variables `DOCKER_BUILDKIT` and `DOCKER_HOST` will be
respectively set to `0` and `$XDG_RUNTIME_DIR/podman/podman.sock`.

So you will be able to run Docker in Podman.

### Wrappers

You can add some wrappers to call some commands transparently :

For example, run molecule without installing it (and its dependencies) on
your system :

```sh
podman_wrappers:
  - command: molecule
    image: gwerlas/molecule
    env:
      MOLECULE_CONTAINERS_BACKEND: podman
    network: host
    security_opt: label=disable
    volume:
      - $HOME/.ansible:/root/.ansible
      - $HOME/.cache/molecule:/root/.cache/molecule
    wrapper_extras:
      env_patterns:
        - ANSIBLE_*
        - MOLECULE_*
      openstack_cli: true
      podman_socket: true
      same_pwd: true
      ssh_auth_sock: true
```

Most of arguments are the same as `podman run` parameters, we support almost
all of the [ansible podman_container module][] arguments as is
(except of aliases and services oriented features).

[ansible podman_container module]: https://docs.ansible.com/ansible/latest/collections/containers/podman/podman_container_module.html

You can add (or remove) the supported parameters list editing the
`podman_wrappers_autofill` variable. You also can editing the default values
editing the `podman_wrappers_values` variable.

Dependencies
------------

None.

Example Playbook
----------------

An exemple of the way to be the more compatible with Docker as You can :

```yaml
---
- name: Docker compatible
  hosts: all
  roles:
    - name: gwerlas.system
    - name: gwerlas.podman
      vars:
        podman_mimic_docker: true
        podman_registries_config:
          unqualified-search-registries:
            - docker.io
```

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
