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

To add support to a new distribution / version, You can define some defaults
if its packages do not work out of the box.

Use the files in the `vars` directory to do it. You can use the
dictionaries below :

- `default_containers_config`
- `default_registries_config`
- `podman_storage_defaults`

The users `podman_*_config` will be merged with the respective
`podman_*_defaults`.

Use this facility only if the distribution packages do not work out of the
box.

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
`tasks/packages/<pkg_mgr>.yml` file, named after the `ansible_facts.pkg_mgr` fact. It is
automatically included by `tasks/packages.yml` when it exists, before the installation.

`tasks/packages/portage.yml` is the current example : it writes the USE flags in
`/etc/portage/package.use/podman` **before** the first `emerge`, so Podman is built right
away with the expected features, and notifies the `Rebuild` handler so an already
installed Podman is rebuilt with `--newuse` when the flags change.

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

Editing documentation
---------------------

### Markdown conventions

Setext headings for levels 1 and 2 (`===` and `---`), dashes for bullets, 80
columns for prose. Tables and code blocks are exempt from the column limit.
Pad table cells so the borders line up, and size each separator row to its
column.

No Markdown linter is configured in this repository, so these are on you.

### Where a rationale lives

A reason is written in exactly one place. From the narrowest home to the
widest :

| Home                     | What it holds                                         |
| ------------------------ | ----------------------------------------------------- |
| Code comment             | what this line does, and under which rule             |
| `CONTRIBUTING` / `docs/` | what the reader has to be able to predict or do       |
| Commit message           | what changes, and why now                             |
| Issue / merge request    | the derivation, the measurements, the paths not taken |
| Upstream documentation   | the rule itself, whenever the rule is not ours        |

Two of those are easy to get wrong, and both make comments longer than they
need to be.

**Cite upstream, never re-derive it.** When the reason is a third-party tool's
behaviour — Portage, apt, systemd, Podman, Jinja — the rule already has a home,
and it is not this repository. Quote one sentence, give the URL, stop. A
reconstruction of your own goes stale without warning the day upstream changes
its mind, and it reads as an opinion of this role when it is in fact an
external constraint.

**A comment summarises, it does not narrate.** It says what the line does and
under which rule. The investigation that led there — when it was observed, what
was measured, which false trail was followed — belongs to the issue and the
commit message, where someone doing archaeology will go looking for it.

Submit your changes
-------------------

Merge request in Gitlab.
