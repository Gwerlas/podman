Development guide
=================

This guide keeps what is specific to the role: how to run its scenarios, its
layout, the rules that are its own. The rest is in the
[engineering handbook][handbook], which binds every contribution here. As an
Ansible role, it is also bound by the family's reference guide, the
[`gwerlas.system` collection's CONTRIBUTING.md][collection-guide], and by the
[principles][collection-principles] that guide enforces. The pages this role's
work touches most:

- [Collection guide][collection-guide]: tags, modules before tasks, a file the
  distribution ships, variables, changelog;
- [Principles][collection-principles]: what users can rely on;
- [Code][handbook-code]: choices, tests, YAML;
- [Git][handbook-git]: commits, issue references;
- [Documentation][handbook-documentation]: who reads what, where a rationale
  lives, Markdown;
- [CI][handbook-ci];
- [Supported platforms][handbook-platforms];
- [Releases][handbook-releases];
- [Issues and merge requests][handbook-mr].

Requirements
------------

Install and configure :

- libvirt / QEMU, with a running storage pool
- molecule
- molecule-plugins
- ansible-lint

The scenarios drive libvirt directly through `community.libvirt` to boot a VM
per platform from an upstream cloud image. There is no Vagrant, and no
container driver either : Podman is the subject of this role, and a rootless
Podman cannot nest inside a rootless container — `newuidmap` has no subuid
range left to map.

`.claude/settings.json` ships a Claude Code hook that runs `ansible-lint` on
every edited YAML file, so a syntax error surfaces at edit time rather than in
the pipeline. It is skipped when the tool is missing, so it never blocks a
contributor who has not installed it.

Adding a new distribution or version
------------------------------------

The list of officially supported platforms lives in
[`molecule/shared/platforms.yml`](molecule/shared/platforms.yml). It is the
single source of truth for both Molecule (one cloud image URL per platform — or
an `image_latest` pointer for a rolling release, resolved at runtime by
`create.yml`) and Galaxy (`galaxy_info.platforms` in `meta/main.yml`).

After editing it, run the sync script to refresh `meta/main.yml` :

```sh
python3 scripts/sync-meta-platforms.py
```

Each scenario's `molecule.yml` then picks a subset by name, with its own
`groups` / `memory` / `vcpus` overrides. Two scenarios wanting the same subset
share one file rather than repeating it — `service` and `wrapper` link their
`molecule.yml` to `default`'s, and what makes a scenario itself is said in its
`converge.yml`. Break a link the day the lists have to differ, not before.

`gentoo-testing` is the Gentoo image again, with the testing branch (`~amd64`)
accepted for podman by `prepare.yml`, because that is where podman 6 is while
the stable branch carries podman 5. It is a platform of `platforms.yml` for the
image and nothing else : it has no `galaxy:` key, as Galaxy lists a distribution
once. `default`'s `molecule.yml` lists it next to `gentoo`, which keeps covering
the stable branch, and the scenarios linked to it boot both.

When a platform enters and leaves the list is the handbook's
[Supported platforms][handbook-platforms] page. An entry leaves
`platforms.yml` and `meta/main.yml` at once, the sync script doing the second.

`molecule/shared/` also hosts the `create.yml`, `destroy.yml` and `prepare.yml`
playbooks that every scenario points at through `provisioner.playbooks`.
Molecule ignores that directory as a scenario because it carries no
`molecule.yml`.

`prepare.yml` stays minimal on purpose : it upgrades the system, points an
archived Debian at `archive.debian.org`, enables the Gentoo binhost, accepts the
testing branch on `gentoo-testing`, reboots when a new kernel came, and stops
there. Nothing converges `gwerlas.system` —
this role only imports its user management — so a converge exercises Podman on
a stock cloud image, which is the point. What a platform needs beyond that
baseline is a gap in the role, not something prepare should paper over.

### Distribution defaults

What [an empty inventory changes][principle-empty] is, for this role, Podman
installed and rootless mode set up for the user running the play. Beyond that
the role corrects the distribution's configuration only where its packages do
not work out of the box. A value the role would merely prefer, or upstream's
default where the distribution chose otherwise, has no place in `vars/`.
`README.md` lists what the role changes on its own ; keep that list in step.

Those corrections go in the files of the `vars` directory. Each configuration
file the role renders reads two dictionaries, named after the file : the
distribution's `_podman_<file>_defaults`, set in `vars/`, and the user's
`podman_<file>_config`, merged over it. `storage.conf` reads a third one
beneath them, `_podman_storage_base`, also set in `vars/` : the base of the
third case of [a file the distribution ships][collection-file]. Copy its keys as
the distribution ships them — leaving out empty lists and tables — and add
nothing it does not set. Where the distribution ships no file and podman cannot
run on one lacking some keys, the base holds podman's own values for them, as
`vars/debian-like.yml` does.

| File                              | Distribution                  | User                       |
| --------------------------------- | ----------------------------- | -------------------------- |
| `/etc/containers/containers.conf` | `_podman_containers_defaults` | `podman_containers_config` |
| `/etc/containers/registries.conf` | `_podman_registries_defaults` | `podman_registries_config` |
| `/etc/containers/storage.conf`    | `_podman_storage_defaults`    | `podman_storage_config`    |
| `/etc/containers/libpod.conf`     | `_podman_libpod_defaults`     | `podman_libpod_config`     |

Look at the `vars/debian11.yml` for example.

The `packages.docker` key deserves a special mention : when it is defined,
the role assumes the distribution provides its own `docker` wrapper (the
`podman-docker` package for most of them). Define it **empty** when the
wrapper comes from somewhere else, like the `wrapper` USE flag on Gentoo :
this prevents the role from creating its own symlink over it.

Target properties : `vars/` files and issue labels
--------------------------------------------------

`tasks/facts.yml` reads a handful of properties off the target and loads
`vars/<value>.yml` for each one it finds, from the least specific to the most :

```text
<os_family>-like.yml                    debian-like, redhat-like, gentoo-like
<os_family><major>-like.yml             redhat7-like
<distribution><major>.yml               debian11, debian12
<distribution>-<release>.yml            ubuntu-jammy
```

The last file loaded wins, so a value lives in the file named after the
property it is *actually* true of, and the narrowest one that still covers
every target it applies to. Refining a value at a narrower level is deliberate
— `debian-like.yml` can set a default that `ubuntu-jammy.yml` overrides. What
to avoid is setting the same value at two levels by accident : the wider one is
then silently dead.

The axis is a property of the **target**, never of this repository's own
layout.

Issue labels follow the same rule, one step wider : an issue carries what it is
true *of* — `gentoo` for something true of Gentoo hosts, `molecule` or `ci` for
the project's own machinery. What an issue never carries is the directory it
happens to touch. An issue true of every target carries no dimension label at
all, and that absence is the correct answer rather than an oversight. On top of
that, one label for the kind : `bug`, `feature` or `tech-debt`.

Package manager specific tasks
------------------------------

If a distribution needs some work before its packages are installed, drop a
`tasks/packages/<pkg_mgr>.yml` file, named after the `ansible_facts.pkg_mgr`
fact. It is automatically included by `tasks/packages.yml` when it exists,
before the installation.

`tasks/packages/portage.yml` is the current example : it writes the USE flags in
`/etc/portage/package.use/podman` **before** the first `emerge`, so Podman is
built right away with the expected features, and notifies the `Rebuild`
handler so an already installed Podman, and whichever of its dependencies
the flags name, is rebuilt with `--newuse --deep` when the flags change.

Run tests
---------

Test the role with its defaults on every supported platform :

```sh
molecule test
```

Test the Docker mimicry, including `docker compose` :

```sh
molecule test -s mimic-docker
```

Test the provisioning of users, images and containers, with the rootless
systemd units and a reboot :

```sh
molecule test -s service
```

Test that a host whose containers run on the units `podman generate systemd`
wrote, left by its prepare step, converges to Quadlet units, on the platforms
whose Podman has Quadlet :

```sh
molecule test -s upgrade
```

Test the wrappers, and what their first call has to create :

```sh
molecule test -s wrapper
```

A scenario always converges the whole role, so none of them runs a tag on its
own. The `tagged-run` job does, for `wrappers` and `provision`, in a container ;
reproduce it with the image it uses :

```sh
podman run --rm -v "$PWD":/role:Z -w /role gwerlas/ansible:debian sh -c '
  ansible-galaxy install -r requirements.yml
  mkdir -p ~/.ansible/roles && ln -sfn "$PWD" ~/.ansible/roles/gwerlas.podman
  ansible-playbook -i localhost, tests/tagged-run.yml --tags wrappers'
```

`users` and `packages` are not in that job : they need a host where `become`
and the package manager work, which a container is not. A change to what those
two tags run is checked by limiting a converge to them by hand.

Every scenario boots the platform list catalogued in
[`molecule/shared/platforms.yml`](molecule/shared/platforms.yml). Comment out
what you don't need in a scenario's `molecule.yml` while developing : a full
run is fourteen VMs.

Gentoo is the slow one, and it cannot be helped : the official binhost is built
against an OpenRC profile, so its Podman carries `-systemd` and is refused by
the systemd profile of the cloud image. The role drives USE flags itself
anyway, which invalidates any binary package. Count about four minutes of
`emerge` on twelve cores.

libvirt connection and storage pool
-----------------------------------

The shared `create.yml` / `destroy.yml` honour four environment variables, with
sensible defaults when unset :

| Variable               | Default              | Purpose                         |
| ---------------------- | -------------------- | ------------------------------- |
| `LIBVIRT_DEFAULT_URI`  | `qemu:///system`     | libvirt connection URI          |
| `LIBVIRT_DEFAULT_POOL` | `default`            | name of the storage pool to use |
| `MOLECULE_MEMORY`      | the platform's value | GB of RAM per VM                |
| `MOLECULE_VCPUS`       | the platform's value | vCPUs per VM                    |

`LIBVIRT_DEFAULT_URI` is the standard libvirt env var; `LIBVIRT_DEFAULT_POOL`
is local to this project but follows the same naming convention. Both are
forwarded into the molecule container by the wrapper (any `LIBVIRT_*` env var
is passed through).

`MOLECULE_MEMORY` and `MOLECULE_VCPUS` override what the scenario asks for,
which is what you want when a run compiles rather than installs. They apply to
every platform of the run, so pair them with `-p` : `default` creates fourteen
VMs, and fourteen times sixteen gigabytes is not a number your workstation has.

```sh
MOLECULE_MEMORY=16 MOLECULE_VCPUS=12 molecule test -p gentoo
```

The pool also caches the cloud images the VMs are cloned from, one per
platform, as `molecule-image-<platform>-<id>.qcow2`. `<id>` fingerprints the
`Last-Modified` and `Content-Length` the publisher serves for the image URL,
read with a `HEAD` before every create. Most platforms track a rolling
`latest/` or `current/` URL whose file name never changes, so the name alone
cannot say whether the cache is still the published image; those two headers
can. A republished image gets a new fingerprint, hence a new volume, and the
one it supersedes is deleted on the same run. `destroy` removes one thing
more : the base image of any platform `platforms.yml` no longer declares.

Both sweeps only ever touch `molecule-image-*` volumes — `LIBVIRT_DEFAULT_POOL`
may well be your own `default` pool, and nothing else in it belongs to molecule.

`qemu:///session` is currently *not* supported by these scenarios : session
mode has no built-in `default` network, and `virsh net-dhcp-leases` would not
find any lease.

Develop / Debug
---------------

```sh
molecule create
molecule converge
molecule login -h <instance_name>
# Do your changes by hand
molecule verify
```

Editing tasks
-------------

`yamllint` and `ansible-lint` leave habits to the author. Most are the
handbook's, in [Code][handbook-code], and the collection guide's, in
[the module, not our own version of it][collection-module]: use the tool that
exists, state choices rather than defaults, quote YAML only where the parser
needs it. Two are this role's.

**Where `command` is the tool that exists.** The module is not always the
obvious one: `ansible.builtin.stat` reads a path's SELinux context with
`get_selinux_context`, `containers.podman.podman_system_info` answers where the
container store lives. `restorecon` is a fair use of
`command` — nothing wraps it — and then the arguments go in `argv`, never in
`cmd`, which is a line to be split and will tear a Jinja expression into pieces
the day one holds a space.

**A scalar wherever the module coerces one.** A parameter declared
`type: list, elements: str` accepts a bare string and wraps it itself, so a
single value is written as one:

```yaml
community.general.portage:
  package: app-containers/podman
```

The list-of-one form reads as a multi-package call nobody trimmed.

Editing templates
-----------------

`ansible-lint` does not read `.j2` files, so a template broken at the syntax
level would ship through a green pipeline. The `j2lint` job covers that, and
only runs when a template changes. To reproduce it locally :

```sh
pip install j2lint==1.3.0
j2lint templates/ --ignore jinja-statements-indentation jinja-statements-delimiter
```

Both ignored rules are explained in `.gitlab-ci.yml`, next to the job.

Whether a template renders the right thing is covered by the scenario that
uses it — `mimic-docker` for `portage.use.j2`, `default` for the
`containers.conf` / `registries.conf` / `storage.conf` family — and those need
a workstation. The pipeline does not run them, so a template change is
reviewed by what it renders, as [Code][handbook-code-test] says.

Editing documentation
---------------------

### Markdown conventions

`markdownlint` checks every `*.md` against the conventions of the handbook's
[Markdown][handbook-markdown] section, recorded, with their rationale, in
`.markdownlint.yaml`. To run it locally:

```sh
markdownlint-cli2 "**/*.md" "!.ansible"
```

The `!.ansible` is for local runs only : `ansible-galaxy install` drops
`gwerlas.system` there, and its documentation is not ours to lint. A CI job
starts from a fresh clone and has no such directory. `CHANGELOG.md` is left out
by `.markdownlint-cli2.yaml`: it is generated, and its HTML anchors and `*`
bullets break rules the role follows.

It fixes much of what it finds on its own with `--fix` — bullets, indentation,
blank lines, bare URLs. What it cannot fix is line length, which is on you.

A line whose overflow contains no space is not reported : a long URL or a
reference-style link definition has nothing to wrap on. That is also the way
out when a link makes a sentence overflow — move the URL to a `[name]:`
definition at the end of the file rather than splitting the link across two
lines.

### Where a rationale lives

Every artifact starts empty: a sentence earns its place when its absence would
cost the reader something precise, not when a home can be found for it. A
reason then lives in exactly one home, the others pointing at it. The handbook's
[Where a rationale lives][handbook-rationale] says how to choose and gives the
three tests by deletion. This role's homes:

| Home                      | What it holds                                       |
| ------------------------- | --------------------------------------------------- |
| Code comment              | what this line does, and under which rule           |
| `CONTRIBUTING` / `README` | what the reader has to be able to predict or do     |
| Commit message            | what changes, and why it is right                   |
| Issue / merge request     | how we know: what was run, measured, tried, dropped |
| Upstream documentation    | the rule itself, whenever the rule is not ours      |

Submit your changes
-------------------

Merge request in Gitlab.

Everything is written in English, as the [handbook][handbook] asks, and commits
follow [Git][handbook-git]: atomic, with their tests and documentation in the
same commit, and the issue referenced from the body only.

A change extends the molecule scenario that fits: an existing one where it
does, `mimic-docker` for anything about the `docker` command, `service` for the
rootless units, `wrapper` for the scripts in `podman_wrappers_path`, `default`
for the role's own defaults.

Changelog
---------

A change a user can notice comes with a fragment in `changelogs/fragments/`,
as the handbook's [Releases][handbook-releases] page says. A fragment is a YAML
file whose keys are the sections of
[antsibull-changelog](https://ansible.readthedocs.io/projects/antsibull-changelog/),
each holding a list of sentences:

```yaml
bugfixes:
  - Render the mirrors of a registry. (`#NN <https://gitlab.com/yoanncolin/ansible/roles/podman/-/issues/NN>`__)
```

An entry that settles an issue ends with that link, written as above and
rendered `[#NN](…)` in `CHANGELOG.md`; the handbook's
[Changelog][handbook-changelog] says why. `CHANGELOG.md` is
generated from the fragments and never edited: the `changelog` job runs
`antsibull-changelog lint`, then `antsibull-changelog generate`, and fails when
`CHANGELOG.md` is not what that gives.

Tagging a release
-----------------

What a tag publishes, and how to number and log a release, is the handbook's
[Releases][handbook-releases] page. Here the `import` job pushes the role to
Ansible Galaxy.

The release merge request runs `antsibull-changelog release --version X.Y.Z
--date YYYY-MM-DD`, since `changelogs/config.yaml` sets the project in "other
project" mode, which has no `galaxy.yml` to take them from. The
`changelog-release` job, which `import` waits for, fails a tag that leaves a
fragment behind or that `changelogs/changelog.yaml` does not hold a release
for; `jobs/changelog-release` runs the same check locally, with
`CI_COMMIT_TAG` set.

[`.gitattributes`](.gitattributes) lists what stays out of the archive users
install: Molecule, CI, the job scripts, the changelog sources, the tagged-run
playbook, linter and editor settings, this guide. A new file that only serves
development belongs in that list.

[handbook]: https://gitlab.com/yoanncolin/handbook/-/blob/main/README.md
[handbook-code]: https://gitlab.com/yoanncolin/handbook/-/blob/main/code.md
[handbook-code-test]: https://gitlab.com/yoanncolin/handbook/-/blob/main/code.md#test-what-the-user-gets
[handbook-git]: https://gitlab.com/yoanncolin/handbook/-/blob/main/git.md
[handbook-documentation]: https://gitlab.com/yoanncolin/handbook/-/blob/main/documentation.md
[handbook-markdown]: https://gitlab.com/yoanncolin/handbook/-/blob/main/documentation.md#markdown
[handbook-rationale]: https://gitlab.com/yoanncolin/handbook/-/blob/main/documentation.md#where-a-rationale-lives
[handbook-ci]: https://gitlab.com/yoanncolin/handbook/-/blob/main/ci.md
[handbook-platforms]: https://gitlab.com/yoanncolin/handbook/-/blob/main/platforms.md
[handbook-releases]: https://gitlab.com/yoanncolin/handbook/-/blob/main/releases.md
[handbook-changelog]: https://gitlab.com/yoanncolin/handbook/-/blob/main/releases.md#changelog
[handbook-mr]: https://gitlab.com/yoanncolin/handbook/-/blob/main/issues-and-merge-requests.md
[collection-guide]: https://gitlab.com/yoanncolin/ansible/collections/system/-/blob/main/CONTRIBUTING.md
[collection-file]: https://gitlab.com/yoanncolin/ansible/collections/system/-/blob/main/CONTRIBUTING.md#a-file-the-distribution-ships
[collection-module]: https://gitlab.com/yoanncolin/ansible/collections/system/-/blob/main/CONTRIBUTING.md#the-module-not-our-own-version-of-it
[collection-principles]: https://gitlab.com/yoanncolin/ansible/collections/system/-/blob/main/docs/principles.md
[principle-empty]: https://gitlab.com/yoanncolin/ansible/collections/system/-/blob/main/docs/principles.md#3-an-empty-inventory-changes-almost-nothing
