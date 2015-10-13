==== Getting Started ====

* cp secrets_template.yml secrets.yml
* Fill out secrets.yml
* install vagrant version 1.7.4+
* install ansible "brew install ansible" for mac

==== To run a local vm ====

* vagrant up

==== To create a ci machine in ec2 ====

* vagrant plugin install vagrant-aws
* vagrant up --provider=aws
