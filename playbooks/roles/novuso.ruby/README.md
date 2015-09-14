# Ansible Role: Ruby

[![Ansible Galaxy](http://img.shields.io/badge/galaxy-novuso.ruby-000000.svg)](https://galaxy.ansible.com/list#/roles/4060)
[![MIT License](http://img.shields.io/badge/license-MIT-003399.svg)](http://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/novuso/ansible-role-ruby.svg)](https://travis-ci.org/novuso/ansible-role-ruby)

An Ansible role that manages Ruby on Ubuntu 14.04

## Requirements

None

## Role Variables

Ansible variables are listed here along with their default values:

`ruby_version` is the default Ruby version to install.

    ruby_version: "2.2.2"

`ruby_install_version` is the version of
[ruby-install](https://github.com/postmodern/ruby-install) to install.

    ruby_install_version: "0.5.0"

`ruby_chruby_version` is the version of
[chruby](https://github.com/postmodern/chruby) to install.

    ruby_chruby_version: "0.3.9"

`ruby_dir` is the path to the default Ruby directory.

    ruby_dir: "/home/{{ ansible_user_id }}/.rubies/ruby-{{ ruby_version }}"

`ruby_bin_dir` is the path to the Ruby bin directory.

    ruby_bin_dir: "{{ ruby_dir }}/bin"

`ruby_gem_exec` is the path to the gem executable.

    ruby_gem_exec: "{{ ruby_bin_dir }}/gem"

`ruby_install_dir` is the path to the installers directory.

    ruby_install_dir: "/home/{{ ansible_user_id }}/.ruby"

`ruby_install_archive_url` is the URL to the ruby-install archive.

    ruby_install_archive_url: "https://github.com/postmodern/ruby-install/archive/v{{ ruby_install_version }}.tar.gz"

`ruby_chruby_archive_url` is the URL to the chruby archive.

    ruby_chruby_archive_url: "https://github.com/postmodern/chruby/archive/v{{ ruby_chruby_version }}.tar.gz"

`ruby_install_download_tar` is the path to download the ruby-install archive.

    ruby_install_download_tar: "{{ ruby_install_dir }}/ruby-install-{{ ruby_install_version }}.tar.gz"

`ruby_chruby_download_tar` is the path to download the chruby archive.

    ruby_chruby_download_tar: "{{ ruby_install_dir }}/chruby-{{ ruby_chruby_version }}.tar.gz"

`ruby_gems` is a list of Ruby gems to manage. Each entry in the list may
designate:

* **name** *required*
* **state** (default is present)
* **user_install** install in local user cache (default is no)
* **version** version number (default is omitted)
* **executable** path to gem (default is `ruby_gem_exec`)
* **gem_source** path to a local gem source (default is omitted)
* **repository** repository to use (default is omitted)
* **pre_release** allow pre-release versions (default is no)
* **include_deps** include dependencies (default is yes)

By default, Ruby gems are not installed:

    ruby_gems: []

## Dependencies

None

## Example Playbook

    ---
    - hosts: all
      vars:
      - ruby_gems:
        - name: "compass"
      roles:
      - novuso.ruby

## License

This is released under the [MIT license](http://opensource.org/licenses/MIT).
