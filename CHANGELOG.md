# gwerlas\.podman Release Notes

**Topics**

- <a href="#v0-9-0">v0\.9\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide">Breaking Changes / Porting Guide</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v0-8-0">v0\.8\.0</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide-1">Breaking Changes / Porting Guide</a>
- <a href="#v0-7-1">v0\.7\.1</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v0-7-0">v0\.7\.0</a>
    - <a href="#release-summary-3">Release Summary</a>
    - <a href="#minor-changes-2">Minor Changes</a>
- <a href="#v0-6-0">v0\.6\.0</a>
    - <a href="#release-summary-4">Release Summary</a>
    - <a href="#minor-changes-3">Minor Changes</a>
- <a href="#v0-5-2">v0\.5\.2</a>
    - <a href="#release-summary-5">Release Summary</a>
    - <a href="#minor-changes-4">Minor Changes</a>
    - <a href="#bugfixes-2">Bugfixes</a>
- <a href="#v0-5-1">v0\.5\.1</a>
    - <a href="#release-summary-6">Release Summary</a>
    - <a href="#bugfixes-3">Bugfixes</a>
- <a href="#v0-5-0">v0\.5\.0</a>
    - <a href="#release-summary-7">Release Summary</a>
    - <a href="#minor-changes-5">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide-2">Breaking Changes / Porting Guide</a>
- <a href="#v0-4-1">v0\.4\.1</a>
    - <a href="#release-summary-8">Release Summary</a>
    - <a href="#bugfixes-4">Bugfixes</a>
- <a href="#v0-4-0">v0\.4\.0</a>
    - <a href="#release-summary-9">Release Summary</a>
    - <a href="#minor-changes-6">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide-3">Breaking Changes / Porting Guide</a>
    - <a href="#bugfixes-5">Bugfixes</a>
- <a href="#v0-3-3">v0\.3\.3</a>
    - <a href="#release-summary-10">Release Summary</a>
    - <a href="#bugfixes-6">Bugfixes</a>
- <a href="#v0-3-2">v0\.3\.2</a>
    - <a href="#release-summary-11">Release Summary</a>
    - <a href="#bugfixes-7">Bugfixes</a>
- <a href="#v0-3-1">v0\.3\.1</a>
    - <a href="#release-summary-12">Release Summary</a>
    - <a href="#bugfixes-8">Bugfixes</a>
- <a href="#v0-3-0">v0\.3\.0</a>
    - <a href="#release-summary-13">Release Summary</a>
    - <a href="#minor-changes-7">Minor Changes</a>
- <a href="#v0-2-0">v0\.2\.0</a>
    - <a href="#release-summary-14">Release Summary</a>
    - <a href="#minor-changes-8">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide-4">Breaking Changes / Porting Guide</a>
- <a href="#v0-1-0">v0\.1\.0</a>
    - <a href="#release-summary-15">Release Summary</a>
    - <a href="#minor-changes-9">Minor Changes</a>

<a id="v0-9-0"></a>
## v0\.9\.0

<a id="release-summary"></a>
### Release Summary

Stop converging gwerlas\.system\, and make wrappers run everywhere\.

<a id="minor-changes"></a>
### Minor Changes

* Configure the Portage USE flags of Podman on Gentoo\. \([\#8](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/8)\)
* Create the source of a bind mount that does not exist yet when a wrapper runs\, and give the wrapper script a shebang\.
* Refuse to mimic Docker when Docker is installed\. \([\#8](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/8)\)
* Require <code>gwerlas\.system</code> 0\.21\.1\. \([\#1](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/1)\)
* Support Debian 13 \(trixie\)\.

<a id="breaking-changes--porting-guide"></a>
### Breaking Changes / Porting Guide

* Stop converging <code>gwerlas\.system</code> as a dependency of the role\. \([\#2](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/2)\) The role still has to be installed\, since it provides the user management\, but a host that relied on this role to apply the whole system configuration has to converge <code>gwerlas\.system</code> itself\.

<a id="bugfixes"></a>
### Bugfixes

* Install <code>acl</code> when <code>podman\_users</code> names a user\, so that provisioning for a user other than the connecting one no longer fails\. \([\#6](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/6)\)
* Label the container store of a rootless user\, wherever its graphroot is\, so that containers can reach their entrypoint on SELinux hosts\. \([\#11](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/11)\)
* Load the facts whatever tag a run is limited to\, so that <code>\-\-tags wrappers</code> no longer fails\. \([\#22](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/22)\)
* Name EPEL\, instead of failing on a missing package\, when <code>podman\-compose</code> is not available on Enterprise Linux\. \([\#5](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/5)\)
* Pick the pull policy of the wrappers from the version of Podman\, so that they run on the Podman 3\.0 of Debian 11\. \([\#19](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/19)\)
* Read the <code>env\_patterns</code> of a wrapper as regular expressions\, as <code>grep</code> does\.
* Reload the unit files only when a unit was written\, so that a run that changes nothing reports no change\. \([\#7](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/7)\)
* Render <code>storage\.conf</code> instead of failing on an undefined variable\, and no longer write an empty <code>\[storage\]</code> table\. \([\#12](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/12)\)
* Set <code>podman\_version</code> on the run that installs Podman\. \([\#21](https\://gitlab\.com/yoanncolin/ansible/roles/podman/\-/issues/21)\)
* Skip an option of a wrapper whose value is null\, instead of emitting a bare flag that swallowed the next option\.

<a id="v0-8-0"></a>
## v0\.8\.0

<a id="release-summary-1"></a>
### Release Summary

Slim down the role and modernize facts access\.

<a id="minor-changes-1"></a>
### Minor Changes

* On Gentoo\, install <code>podman\-compose</code> and use <code>nftables</code> as the default firewall driver\.
* Write a static header\, <code>Ansible managed \- do not edit</code>\, in the generated files\, so that they no longer change from one run to the next\.

<a id="breaking-changes--porting-guide-1"></a>
### Breaking Changes / Porting Guide

* Mount the Podman socket on <code>/run/podman/podman\.sock</code>\, instead of <code>/run/docker\.sock</code>\, in the containers of the wrappers that need it\.
* Stop loading the <code>ip\_tables</code> and <code>tun</code> kernel modules\, stop writing the Portage USE flags of iptables\, and stop refusing to mimic Docker when Docker is installed\.

<a id="v0-7-1"></a>
## v0\.7\.1

<a id="release-summary-2"></a>
### Release Summary

Set DBUS environment variable on service management\.

<a id="bugfixes-1"></a>
### Bugfixes

* Set <code>DBUS\_SESSION\_BUS\_ADDRESS</code> when managing the systemd service of a rootless container\.

<a id="v0-7-0"></a>
## v0\.7\.0

<a id="release-summary-3"></a>
### Release Summary

Rewrite image provisioning\.

<a id="minor-changes-2"></a>
### Minor Changes

* Declare Enterprise Linux 10 and Gentoo among the supported platforms\.
* Provision images on their own with <code>podman\_images</code>\.

<a id="v0-6-0"></a>
## v0\.6\.0

<a id="release-summary-4"></a>
### Release Summary

Enable podman login on image pull\.

<a id="minor-changes-3"></a>
### Minor Changes

* Log in to a registry when pulling the image of a container\, with the <code>username</code> and <code>password</code> keys of a <code>podman\_containers</code> entry\.

<a id="v0-5-2"></a>
## v0\.5\.2

<a id="release-summary-5"></a>
### Release Summary

Retry images downloads on network failures\.

<a id="minor-changes-4"></a>
### Minor Changes

* Run the package installation and the user management alone with the <code>packages</code> and <code>users</code> tags\.

<a id="bugfixes-2"></a>
### Bugfixes

* Retry the download of the images on network failures\.

<a id="v0-5-1"></a>
## v0\.5\.1

<a id="release-summary-6"></a>
### Release Summary

Fix the check mode\.

<a id="bugfixes-3"></a>
### Bugfixes

* Run the Podman and Docker version probes in check mode too\, so that <code>\-\-check</code> no longer fails on them\.

<a id="v0-5-0"></a>
## v0\.5\.0

<a id="release-summary-7"></a>
### Release Summary

Add resources provisioning\.

<a id="minor-changes-5"></a>
### Minor Changes

* Provide the <code>podman\_version</code> and <code>podman\_packages</code> facts without changing the node\, with <code>tasks\_from facts</code>\.
* Provision networks \(<code>podman\_networks</code>\) and containers \(<code>podman\_containers</code>\)\, the latter as systemd services\.
* Run the provisioning alone with the <code>provision</code> tag\.

<a id="breaking-changes--porting-guide-2"></a>
### Breaking Changes / Porting Guide

* The <code>podman\_current\_version</code> fact is now <code>podman\_version</code>\.

<a id="v0-4-1"></a>
## v0\.4\.1

<a id="release-summary-8"></a>
### Release Summary

Fix system users\' home dir permissions\.

<a id="bugfixes-4"></a>
### Bugfixes

* Fix the permissions of the home directory of system users\.

<a id="v0-4-0"></a>
## v0\.4\.0

<a id="release-summary-9"></a>
### Release Summary

Fix system users management\.

<a id="minor-changes-6"></a>
### Minor Changes

* Create the users of <code>podman\_users</code> that do not exist yet through the <code>gwerlas\.system</code> role\, unless <code>podman\_create\_missing\_users</code> is <code>false</code>\.
* Run the rootless tasks alone with <code>tasks\_from rootless</code>\.

<a id="breaking-changes--porting-guide-3"></a>
### Breaking Changes / Porting Guide

* <code>podman\_users</code> is now a list of objects with a <code>name</code> and optional <code>home</code>\, <code>uid</code>\, <code>subuid\_starts</code>\, <code>subuid\_length</code>\, <code>subgid\_starts</code> and <code>subgid\_length</code> keys\, instead of a list of login names\.

<a id="bugfixes-5"></a>
### Bugfixes

* Fix the management of the users of <code>podman\_users</code>\, their home directory and their subordinate user and group ID ranges\.

<a id="v0-3-3"></a>
## v0\.3\.3

<a id="release-summary-10"></a>
### Release Summary

Flush handlers on subuid modification\.

<a id="bugfixes-6"></a>
### Bugfixes

* Migrate Podman\'s system right after a change of the subordinate user or group IDs\, so that the change takes effect during the run\.

<a id="v0-3-2"></a>
## v0\.3\.2

<a id="release-summary-11"></a>
### Release Summary

Retry packages installation on network failures\.

<a id="bugfixes-7"></a>
### Bugfixes

* Retry the installation of the packages on network failures \(<code>podman\_retries</code>\)\.

<a id="v0-3-1"></a>
## v0\.3\.1

<a id="release-summary-12"></a>
### Release Summary

Fix module kernel loading\.

<a id="bugfixes-8"></a>
### Bugfixes

* Load the <code>ip\_tables</code> kernel module persistently and\, on Gentoo\, build iptables with its <code>nftables</code> USE flag\.

<a id="v0-3-0"></a>
## v0\.3\.0

<a id="release-summary-13"></a>
### Release Summary

Add wrappers\.

<a id="minor-changes-7"></a>
### Minor Changes

* Install wrappers that run a command in a container through Podman \(<code>podman\_wrappers</code>\, <code>podman\_wrappers\_path</code>\, <code>podman\_wrappers\_values</code>\)\.

<a id="v0-2-0"></a>
## v0\.2\.0

<a id="release-summary-14"></a>
### Release Summary

Add Gentoo support\.

<a id="minor-changes-8"></a>
### Minor Changes

* Support Gentoo\.

<a id="breaking-changes--porting-guide-4"></a>
### Breaking Changes / Porting Guide

* Require Ansible 2\.10 or later\.

<a id="v0-1-0"></a>
## v0\.1\.0

<a id="release-summary-15"></a>
### Release Summary

Initial version\.

<a id="minor-changes-9"></a>
### Minor Changes

* Install Podman\, with the Compose and Toolbox packages on request \(<code>podman\_compose\_install</code>\, <code>podman\_toolbox\_install</code>\)\.
* Make Podman a drop\-in replacement for Docker with <code>podman\_mimic\_docker</code>\.
* Set up Podman in rootless mode for the users of <code>podman\_users</code>\.
* Write <code>/etc/containers/containers\.conf</code>\, <code>registries\.conf</code>\, <code>storage\.conf</code> and <code>libpod\.conf</code> from the <code>podman\_containers\_config</code>\, <code>podman\_registries\_config</code>\, <code>podman\_storage\_config</code> and <code>podman\_libpod\_config</code> dictionaries\, and leave the distribution\'s files alone when none is set\.
