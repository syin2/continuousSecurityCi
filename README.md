==== To create a docker-machine in ec2 ====

* cp secrets_template.yml secrets.yml
* Fill out secrets.yml
* bin/make_ec2_vm <name of your vm without underscores>
* eval "$(docker-machine env <name of your vm>)"
* docker-compose up -d
