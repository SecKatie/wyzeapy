<!--
SPDX-FileCopyrightText: 2021 Katie Mulliken <katie@mulliken.net>

SPDX-License-Identifier: GPL-3.0-only
-->

# Changelog
All notable changes to this project will be documented in this file.
See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.

- - -
## 0.5.0..0.5.26 - 2023-12-08

### Bug Fixes

* Update device UUID extraction logic in BaseService
* Add CodeQL configuration for improved security analysis
* Better handle token expiration (#83)
* Update notification endpoint (#81)
* Update motion properties (#82)
* Fix aiohttp conflict with homeassistant
* Fixed toggles and properties for many camera models
* Fix value error that might occur under certain conditions
* Pass mutex to DeviceUpdater (#64)
* Guard against empty queue in update_manager
* Fix lock querying - update access_token (#57)
* Protect update function in update_manager.py (#54)
* Handle sun match (#49)
* Remove color mode change (#47)

### Features

* Add support for UnLocking and Locking states for Wyze Lock (#75)
* Add support for outdoor plug energy sensors (#79)
* Add API Key/ID support (#70)
* Support for camera sirens (#42)
* Add option to unload entities (#37)
* Add cloud fallback when local control is unavailable (#35)
* Support for lightstrips (#32)
* Local control for color bulbs (#31)
* Support for Floodlight (#45)
* Support music mode (#44)
* Add global local control option (#38)
* Update manager - use a mutex (#60)
* Re-enable and fix thermostat presets (#59)
* Add Camera motion detection switch (#56)
* Handle music mode switch (#55)
* Add new Wyze wall switch (#52)
* Add notification property (#46)

### Dependencies

* Bump aiohttp from 3.8.1 to 3.8.5 (#69)
* Bump aiohttp from 3.10.9 to 3.10.11
* Bump idna from 3.6 to 3.7 (#90)
* Bump aiohttp from 3.9.3 to 3.9.4 (#89)

### Continuous Integration

* Add publish workflow and adjust job names
* Add prerelease github workflow

### Miscellaneous Chores

* Bump patch version
* Update repository name
* Update poetry
* Fix wall switch service compatibility
* Update exceptions handling

- - -
## 0.4.4..0.5.0 - 2021-10-06


### Continuous Integration

6751e7 - Add Semgrep CI - semgrep.dev on behalf of @JoshuaMulliken
cd937f - add codeql-analysis.yml - Katie Mulliken

### Bug Fixes

19146d - update manager inconsistencies and infinite loop (#1)* refactor: update_manager: Add some consistency to the updates_per_interval valuechange the name of this argument so that it is more clear that this should be the time between updates. Additionally add a doc string to give some context.This also means that we'll need to calculate the interval/updates_per_interval to get the actual countdown time.* fix: update_manger: fix the infinite loop while trying to conduct a backoffthis infinite loop was created because of an inconsitency in how the updates_per_interval value was being used between the classes. Now that it's being used an intended, the value should be used directly in these values.A smaller updates_per_interval will equate to a longer time between updates for a device. - Joe Schubert
4e6d3e - ensure that updates_per_interval cannot be reduced to zero - Katie Mulliken

### Features

da4455 - Utilize an update_manager to alleviate load on wyze's api (#1)Co-authored-by: Katie Mulliken <katie@mulliken.net> - Joe Schubert

### Miscellaneous Chores

a92950 - bump version to stable - Josh Mulliken
82b588 - bump version - Josh Mulliken
ed7eb5 - bump version - Katie Mulliken
fea63d - correct license information - Josh Mulliken

- - -
## 0.4.4 - 2021-09-27


### Bug Fixes

f08f6b - fix lock status being flipped - Katie Mulliken


### Miscellaneous Chores

b7cd51 - bump version in setup.cfg - Katie Mulliken


- - -
## 0.4.3 - 2021-09-26


### Bug Fixes

88e1bb - modify pypi version number - Katie Mulliken


- - -
## 0.4.2 - 2021-09-26


### Bug Fixes

8e26ff - remove redundent return before the logging functions - Katie Mulliken


### Documentation

532552 - update changelog to fit what cocogitto expects - Katie Mulliken


- - -
## 0.4.0..0.4.1 - 2021-09-26


### Miscellaneous Chores

8c9f7a - cleanup old files - Katie Mulliken
726a46 - bump version - Katie Mulliken

### Features

8bff85 - add logging for get, patch, and delete - Katie Mulliken

