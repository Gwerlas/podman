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

Dependencies
------------

Everything is in the [requirements.yml](requirements.yml) file.

### Collections

For obvious reasons, You'll need the [Containers.Podman][] collection :

```sh
ansible-galaxy collection install containers.podman
```

To be able to manage the required kernel modules, You'll need to have the
[Community.General][] collection version 8.2 or upper to be installed :

```sh
ansible-galaxy collection install community.general
```

[Community.General]: https://docs.ansible.com/ansible/latest/collections/community/general/index.html
[Containers.Podman]: https://docs.ansible.com/ansible/latest/collections/containers/podman/index.html

### Roles

The `gwerlas.system` is used for user management when
`podman_create_missing_users` is `true`.

Be sure to have it installed :

```sh
ansible-galaxy install gwerlas.system
```

It has to be installed, but this role never converges it : we only import its
user management tasks, and only when there is a missing user to create. Your
nodes get Podman and what this role needs to set it up, nothing else.

If You want it, play it yourself, it may help You to prepare your node :

```yaml
- name: My playbook
  hosts: all
  roles:
    - role: gwerlas.system
    - role: gwerlas.podman
```

Facts
-----

Defined facts of this role :

- `podman_version`
- `podman_packages`

You can get the facts only, without doing any changes on your nodes :

```yaml
- name: My playbook
  hosts: all
  tasks:
    - name: Get facts
      ansible.builtin.import_role:
        name: gwerlas.podman
        tasks_from: facts

    - name: Display
      ansible.builtin.debug:
        var: podman_packages
```

Tags
----

You can filter on some specific tasks using this tags :

- `packages`
- `provision` : Provisioned containers, images and networks
- `users` : Rootless directories, subgids and subuids
- `wrappers` : [Wrappers](#wrappers)

Role Variables
--------------

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
podman_compose_install: false
podman_toolbox_install: false

podman_mimic_docker: false

podman_create_missing_users: true
podman_users:
  - name: "{{ ansible_facts.user_id }}"

podman_wrappers: []
podman_wrappers_path: /usr/local/bin
```

### Podman rootless

To let some users using Podman in rootless mode, the `podman_users` have to be
a list of objects formed like this :

```yaml
podman_users:
  - name: jdoe            # Unix login name (required)
    home: /home/jdoe      # Got from user entries if missing
    uid: 1000             # Used only for users not yet created system wide
    subuid_starts: 100000 # Generated from the user id by default
    subuid_length: 50000  # 65536 by default
    subgid_starts: 100000 # Same as subuid_starts by default
    subgid_length: 50000  # Same as subuid_length by default
```

`subuid_*` and `subgid_*` are this role's own. Every other key goes to
`gwerlas.system`, which creates the user, so an entry takes anything the
[`ansible.builtin.user`][user module] module takes — `shell`, `groups`,
`password_lock`, `system`, `state` — plus `authorized_keys` :

```yaml
podman_users:
  - name: nginx
    system: true
    uid: 300
    shell: /usr/bin/nologin
    password_lock: true
    home: /data/web
    create_home: false
```

[user module]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/user_module.html

Because podman store its data in the user's home directory, we will
create it if missing.

On a host enforcing SELinux, a container store landing outside `/home` — a
`home` of its own, or a `graphroot` named in `podman_storage_config` — is
declared equivalent to the path it would have under `/home`, and relabelled, so
the system reads it as the store it is. Without that, the containers We
provision for that user cannot start. The home itself is never touched : its
context is yours to set.

You can add users quickly calling the `rootless` task alone :

```yaml
---
- name: Add a user for podman rootless usage
  hosts: all
  vars:
    podman_users:
      - name: jdoe
        uid: 300
  tasks:
    - name: Add John Doe
      ansible.builtin.import_role:
        name: gwerlas.podman
        tasks_from: rootless
```

#### Unexisting users

For users that doesn't yet exist, we will create them for You through the
`gwerlas.system` role.

To disable missing user creation, set `podman_create_missing_users` to `false`.
In this case, You have to set the `uid` property for each missing users.

#### Containers running at boot

Declaring a user `system: true` also enables systemd lingering for it, so its
user instance starts with the machine. The rootless units generated for
`podman_containers` need it : without lingering they only run while that user
has a session open, and `enabled: true` on a container means "until they log
out".

### Podman configuration

By default, we let the configuration files of the distribution inchanged.

Except for the Debian 11 containers settings who does not work out of the box.

To use a customized configuration, use `podman_*_config` settings.

#### Containers

Use the `podman_containers_config` dictionary to populate the
`/etc/containers/containers.conf` file following the same structure as the toml
described in [`containers.conf`][] man page.

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

For Debian 11 only, we overwrite the distribution defaults by the
configuration above.

#### Registries

**NOTE** We do not support the deprecated version 1 format.

Use the `podman_registries_config` dictionary to populate the
`/etc/containers/registries.conf` file following the same structure as the toml
described in [`registries.conf`][] man page.

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

Use the `podman_storage_config` dictionary to populate the
`/etc/containers/storage.conf` file following the same structure as the toml
described in [`storage.conf`][] man page.

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

Use the `podman_libpod_config` dictionary to populate the
`/etc/containers/libpod.conf` file following the same structure as the toml
described in [`libpod.conf`][] man page.

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

For Debian 11 only, we overwrite the distribution defaults by the
configuration above.

### Optional features

The `podman_compose_install`, `podman_toolbox_install` and `podman_mimic_docker`
options enable extra features that rely on distribution packages. The exact
package names mapped to each option are defined in the [`vars/`](vars/) files
of this role.

When the corresponding package is **not available** for the target distribution
(for example, `podman-toolbox` is not packaged on Gentoo), the option is
silently a no-op: nothing is installed and no error is raised. This keeps the
role usable across distributions with uneven packaging coverage, at the cost of
masking missing features — check the relevant `vars/` file if You're unsure
whether a given option is actually wired up for your distribution.

### Podman compose

The `podman_compose_install` set to `true` will install `podman-compose` if it
is available for the distribution of the targetted host.

On Enterprise Linux that package comes from EPEL, and We do not enable a
third-party repository on your hosts : install `epel-release` yourself, or the
role stops with a message telling You so. Fedora ships the package in its own
repositories, and needs nothing.

### Podman toolbox

The `podman_toolbox_install` set to `true` will install `podman-toolbox` if it
is available for the distribution of the targetted host.

### Mimic Docker

#### Docker in the $PATH

You can mimic Docker throw the `podman_mimic_docker` parameter set to `true`. A
`docker` command is then provided in the `$PATH`, by the most native mean
available on the target Linux distribution :

| Distribution                   | Provided by                                       |
| ------------------------------ | ------------------------------------------------- |
| Debian like, RedHat like, Arch | the `podman-docker` package                       |
| Gentoo like                    | the `wrapper` USE flag on `app-containers/podman` |
| Others (Debian 11, RedHat 7)   | a `docker` symlink to `podman`, made by this role |

So the scripts calling `docker` will transparently use `podman` instead, or almost.

`docker compose` follows, as long as `podman_compose_install` is set to `true`
and the installed Podman is `4.7` or upper, which routes it to `podman-compose`
by itself.

If a **real** Docker is already installed on the target host, the role fails
instead of overwriting its `docker` command : remove Docker, or set
`podman_mimic_docker` to `false`.

#### Daemon socket

If the installed version of Podman is `3.0` or upper, the service will be
enabled for each `podman_users` and the environment variables `DOCKER_BUILDKIT`
and `DOCKER_HOST` will be respectively set to `0` and
`$XDG_RUNTIME_DIR/podman/podman.sock`.

So you will be able to run Docker in Podman.

### Wrappers

You can add some wrappers to call some commands transparently :

For example, run molecule without installing it (and its dependencies) on
your system :

```yaml
podman_wrappers:
  - command: molecule
    image: gwerlas/molecule
    env:
      CONTAINER_CONNECTION: docker
      MOLECULE_CONTAINERS_BACKEND: podman
    interactive: true
    network: host
    security_opt: label=disable
    volume:
      - $HOME/.cache/molecule:/root/.cache/molecule
      - $HOME/.vagrant.d:/root/.vagrant.d
      - /run/libvirt:/run/libvirt
      - /var/lib/libvirt:/var/lib/libvirt
      - /var/tmp:/var/tmp
    wrapper_extras:
      env_patterns:
        - ^ANSIBLE_
        - ^MOLECULE_
      openstack_cli: true
      podman_socket: true
      same_pwd: true
      ssh_auth_sock: true
```

Most of arguments are the same as `podman run` parameters, we support almost
all of the [ansible podman_container module][] arguments plus :

- `username`: Username to use when authenticating to remote registries.
- `password`: Password to use when authenticating to remote registries.

[ansible podman_container module]: https://docs.ansible.com/ansible/latest/collections/containers/podman/podman_container_module.html

You can add (or remove) the supported parameters list editing the
`podman_wrappers_autofill` variable. You also can editing the default values
editing the `podman_wrappers_values` variable.

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
```

License
-------

[BSD 3-Clause License](LICENSE).
