# -*- mode: ruby -*-
# vi: set ft=ruby :
require 'yaml'

SECRETS = YAML.load_file(File.expand_path(File.join(File.dirname(__FILE__), "./secrets.yml")))

def get_secret(key)
  SECRETS.has_key?(key) ? SECRETS[key] : raise("Your secrets file is missing your #{key}")
end

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 8153, host: 8153
  config.vm.network "forwarded_port", guest: 8154, host: 8154

  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 3
  end

  config.vm.provider :aws do |aws, override|
    aws.access_key_id = get_secret("aws_access_key")
    aws.secret_access_key = get_secret("aws_secret_key")
    aws.region = "us-east-1"
    aws.instance_type = "t2.medium"
    aws.keypair_name = get_secret("aws_keypair_name")
    aws.security_groups = ["sg-da566fbd"]
    aws.subnet_id = get_secret("aws_subnet_id")
    aws.associate_public_ip = true
    aws.ami = "ami-d05e75b8"
    override.ssh.username = "ubuntu"
    override.ssh.private_key_path = get_secret("local_aws_ssh_private_key_path")
    override.vm.box_url = "https://github.com/mitchellh/vagrant-aws/raw/master/dummy.box"
    override.vm.box = "dummy"
    override.nfs.functional = false
  end

  config.vm.provision "ansible" do |ansible|
    ansible.sudo = true
    ansible.limit = 'all'
    ansible.playbook = "playbooks/sudo.yml"
    ansible.extra_vars = {
      GOCD_ADMIN_EMAIL: 'jim@thoughtworks.com'
    }
  end

  config.vm.provision "ansible" do |ansible|
    ansible.limit = 'all'
    ansible.playbook = "playbooks/sudoless.yml"
  end
end
