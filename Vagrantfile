# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.provider "docker" do |docker|
    docker.image = "redis"
    docker.name = "redis-container"
    docker.has_ssh = true
  end
end
