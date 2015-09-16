#!/usr/bin/env python
from gomatic import *

configurator = GoCdConfigurator(HostRestClient("localhost:8153"))
pipeline = configurator \
    .ensure_pipeline_group("pretend") \
    .ensure_replacement_of_pipeline("first_pipeline") \
    .set_git_url("http://git.url")
stage = pipeline.ensure_stage("a_stage")
job = stage.ensure_job("a_job")
job.add_task(ExecTask(['thing']))

configurator.save_updated_config()

pipeline = configurator\
	.ensure_pipeline_group("pretend")\
	.ensure_replacement_of_pipeline("pretend_catalog_service")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_catalog_service")
stage = pipeline.ensure_stage("Test")
job = stage.ensure_job("UnitTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec']))
stage = pipeline.ensure_stage("DeployStaging")
job = stage.ensure_job("Deploy")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake deploy_dev']))

pipeline = configurator\
	.ensure_pipeline_group("pretend")\
	.ensure_replacement_of_pipeline("pretend_pricing_service")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_pricing_service")
stage = pipeline.ensure_stage("DeployStaging")
job = stage.ensure_job("Deploy")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake deploy_dev']))

pipeline = configurator\
	.ensure_pipeline_group("pretend")\
	.ensure_replacement_of_pipeline("pretend_web_app")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_web_app")
stage = pipeline.ensure_stage("DeployStaging")
job = stage.ensure_job("Deploy")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake deploy_dev']))

configurator.save_updated_config(save_config_locally=True, dry_run=True)
