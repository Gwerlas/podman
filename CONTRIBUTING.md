Development guide
=================

This role should not need any external settings to work.

Requirements
------------

Install and configure :

- libvirt / QEMU, with a running storage pool
- python3-jmespath
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
share one file rather than repeating it — `service` links its `molecule.yml` to
`default`'s, and what makes the scenario itself is said in its `converge.yml`.
Break the link the day the lists have to differ, not before.

Supported does not mean current : a platform stays in the list as long as we
can still test it, whatever its upstream end of life. What we cannot do is
guarantee one whose packages are no longer reachable, and that is where an
entry leaves both files at once.

`molecule/shared/` also hosts the `create.yml`, `destroy.yml` and `prepare.yml`
playbooks that every scenario points at through `provisioner.playbooks`.
Molecule ignores that directory as a scenario because it carries no
`molecule.yml`.

`prepare.yml` stays minimal on purpose : it upgrades the system, enables the
Gentoo binhost, reboots when a new kernel came, and stops there. Nothing
converges `gwerlas.system` — this role only imports its user management — so a
converge exercises Podman on a stock cloud image, which is the point. What a
platform needs beyond that baseline is a gap in the role, not something prepare
should paper over.

### Distribution defaults

You can define some defaults if the distribution packages do not work out of
the box.

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
`tasks/packages/<pkg_mgr>.yml` file, named after the `ansible_facts.pkg_mgr`
fact. It is automatically included by `tasks/packages.yml` when it exists,
before the installation.

`tasks/packages/portage.yml` is the current example : it writes the USE flags in
`/etc/portage/package.use/podman` **before** the first `emerge`, so Podman is
built right away with the expected features, and notifies the `Rebuild`
handler so an already installed Podman is rebuilt with `--newuse` when the
flags change.

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

Every scenario boots the same platform list, catalogued in
[`molecule/shared/platforms.yml`](molecule/shared/platforms.yml). Comment out
what you don't need in a scenario's `molecule.yml` while developing : a full
run is thirteen VMs.

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
every platform of the run, so pair them with `-p` : `default` creates thirteen
VMs, and thirteen times sixteen gigabytes is not a number your workstation has.

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

`yamllint` and `ansible-lint` leave two habits to the author, both about how a
value is written rather than what it means.

**A scalar wherever the module coerces one.** A parameter declared
`type: list, elements: str` accepts a bare string and wraps it itself, so a
single value is written as one:

```yaml
community.general.portage:
  package: app-containers/podman
```

The list-of-one form reads as a multi-package call nobody trimmed.

**Quotes only where YAML needs them.** `app-containers/podman`, `~amd64`,
`podman` and file paths are plain scalars and stay bare. Quote when the parser
would otherwise take the value for something else: a string shaped like a
boolean or a number (`"yes"`, `"123"`), a value opening on `%`, `*`, `&`, `?`
or `:`, one holding a `#` or a colon followed by a space, and a Jinja
expression that starts the value — `"{{ var }}"`, which YAML reads as a flow
mapping without them.

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

Linting only proves a template *compiles*. Whether it renders the right thing
is covered by the scenario that uses it — `mimic-docker` for `portage.use.j2`,
`default` for the `containers.conf` / `registries.conf` / `storage.conf`
family — and those need a workstation. So review a template change by looking
at what it produces, not by trusting the pipeline.

Editing documentation
---------------------

### Markdown conventions

`markdownlint` checks every `*.md`. The conventions this role follows — setext
headings for levels 1 and 2, dashes for bullets, 80 columns for prose with
tables and code blocks exempt — are recorded, with their rationale, in
`.markdownlint.yaml`. To run it locally :

```sh
markdownlint-cli2 "**/*.md" "!.ansible"
```

The `!.ansible` is for local runs only : `ansible-galaxy install` drops
`gwerlas.system` there, and its documentation is not ours to lint. A CI job
starts from a fresh clone and has no such directory.

It fixes much of what it finds on its own with `--fix` — bullets, indentation,
blank lines, bare URLs. What it cannot fix is line length, which is on you.

A line whose overflow contains no space is not reported : a long URL or a
reference-style link definition has nothing to wrap on. That is also the way
out when a link makes a sentence overflow — move the URL to a `[name]:`
definition at the end of the file rather than splitting the link across two
lines.

Pad table cells so the borders line up, and size each separator row to its
column.

### Where a rationale lives

Every artifact starts empty : a sentence earns its place when its absence would
cost the reader something precise, not when a home can be found for it. A
reason then lives in exactly one of these, the others pointing at it :

| Home                     | What it holds                                       |
| ------------------------ | --------------------------------------------------- |
| Code comment             | what this line does, and under which rule           |
| `CONTRIBUTING` / `README`| what the reader has to be able to predict or do     |
| Commit message           | what changes, and why it is right                   |
| Issue / merge request    | how we know: what was run, measured, tried, dropped |
| Upstream documentation   | the rule itself, whenever the rule is not ours      |

Write in that order, narrowest first. A merge request is written **against**
its commits, not from the same head of context : after one opening sentence
naming what it does, it holds only what the diff and the commit messages do not
already say. A one-line pointer beats a restatement every time.

Two boundaries, two tests, both by deletion.

**A comment summarises, it does not narrate.** Remove everything written in the
past tense — when it was observed, what was measured, which false trail was
followed. What is left is the rule.

**A commit is knowable without running anything.** Remove from the merge
request every sentence that would already be true had the work never run : it
belongs to the commit. Remove from the commit every sentence that only became
true by running something : it belongs to the merge request.

**Cite upstream, never re-derive it.** When the reason is a third-party tool's
behaviour — Portage, apt, systemd, Podman, Jinja — quote one sentence, give the
URL, stop. A reconstruction of your own goes stale the day upstream changes its
mind, and reads as this role's opinion when it is an external constraint.

Submit your changes
-------------------

Merge request in Gitlab.

Everything that lands in the repository or in GitLab is written in English —
code, comments, commit messages, `README.md`, this file, and the title and body
of every issue and merge request. A conversation held in another language stops
at the artifact.

A change comes with its tests and its documentation, in the same commit. A new
variable, or a change in behaviour, is not finished until :

- a molecule scenario exercises it — an existing one where it fits,
  `mimic-docker` for anything about the `docker` command, `service` for the
  rootless units, `default` for the role's own defaults;
- the user-facing half is written in `README.md` : what the variable does, its
  default, an example;
- the reasoning a future maintainer will need — an upstream constraint, a
  Portage quirk, why two tasks must run in that order — goes in a code comment
  or in this file, not in the user documentation.

Keeping the three together is what makes a commit reviewable on its own : a
change that arrives without its test looks finished when it is not, and one
that arrives without its reason forces the next reader to guess.

The issue is referenced from the commit body, and only from there. `Closes #3`
if the commit settles the whole ticket; `Relates to #3` if it settles one of
the three things the ticket asks for, so the other two stay visible. Never the
bare number on a line of its own : git strips a line opening on `#` as a
comment whenever the message goes through an editor, and the reference vanishes
without a word. `README.md` never carries an issue number — a user can do
nothing with it, and it goes stale the day the issue closes.
