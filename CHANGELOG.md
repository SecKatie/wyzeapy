<!--
SPDX-FileCopyrightText: 2021 Joshua Mulliken <joshua@mulliken.net>

SPDX-License-Identifier: GPL-3.0-only
-->

# Changelog
All notable changes to this project will be documented in this file.
See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.

- - -
## 0.4.4..0.5.0 - 2021-10-06


### Continuous Integration

6751e7 - Add Semgrep CI - semgrep.dev on behalf of @JoshuaMulliken
cd937f - add codeql-analysis.yml - Joshua Mulliken

### Bug Fixes

19146d - update manager inconsistencies and infinite loop (#1)* refactor: update_manager: Add some consistency to the updates_per_interval valuechange the name of this argument so that it is more clear that this should be the time between updates. Additionally add a doc string to give some context.This also means that we'll need to calculate the interval/updates_per_interval to get the actual countdown time.* fix: update_manger: fix the infinite loop while trying to conduct a backoffthis infinite loop was created because of an inconsitency in how the updates_per_interval value was being used between the classes. Now that it's being used an intended, the value should be used directly in these values.A smaller updates_per_interval will equate to a longer time between updates for a device. - Joe Schubert
4e6d3e - ensure that updates_per_interval cannot be reduced to zero - Joshua Mulliken

### Features

da4455 - Utilize an update_manager to alleviate load on wyze's api (#1)Co-authored-by: Joshua Mulliken <joshua@mulliken.net> - Joe Schubert

### Miscellaneous Chores

a92950 - bump version to stable - Josh Mulliken
82b588 - bump version - Josh Mulliken
ed7eb5 - bump version - Joshua Mulliken
fea63d - correct license information - Josh Mulliken

- - -
## 0.4.4 - 2021-09-27


### Bug Fixes

f08f6b - fix lock status being flipped - Joshua Mulliken


### Miscellaneous Chores

b7cd51 - bump version in setup.cfg - Joshua Mulliken


- - -
## 0.4.3 - 2021-09-26


### Bug Fixes

88e1bb - modify pypi version number - Joshua Mulliken


- - -
## 0.4.2 - 2021-09-26


### Bug Fixes

8e26ff - remove redundent return before the logging functions - Joshua Mulliken


### Documentation

532552 - update changelog to fit what cocogitto expects - Joshua Mulliken


- - -
## 0.4.0..0.4.1 - 2021-09-26


### Miscellaneous Chores

8c9f7a - cleanup old files - Joshua Mulliken
726a46 - bump version - Joshua Mulliken

### Features

8bff85 - add logging for get, patch, and delete - Joshua Mulliken

