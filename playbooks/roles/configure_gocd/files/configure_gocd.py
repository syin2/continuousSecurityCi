#!/usr/bin/env python
from gomatic import *
import os

CF_EMAIL = os.environ['CF_EMAIL']
CF_PASSWORD = os.environ['CF_PASSWORD']

configurator = GoCdConfigurator(HostRestClient("localhost:8153"))

pipeline = configurator\
	.ensure_pipeline_group("pretend")\
	.ensure_replacement_of_pipeline("pretend_catalog_service")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_catalog_service")
pipeline.ensure_unencrypted_secure_environment_variables({"CF_EMAIL": CF_EMAIL, "CF_PASSWORD": CF_PASSWORD})
stage = pipeline.ensure_stage("Test")
job = stage.ensure_job("UnitTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec']))
stage = pipeline.ensure_stage("DeployStaging")
job = stage.ensure_job("Deploy")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake deploy_dev']))

pipeline = configurator\
	.ensure_pipeline_group("pretend")\
	.ensure_replacement_of_pipeline("pretend_pricing_service")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_pricing_service")
pipeline.ensure_unencrypted_secure_environment_variables({"CF_EMAIL": CF_EMAIL, "CF_PASSWORD": CF_PASSWORD})
stage = pipeline.ensure_stage("UnitTest")
job = stage.ensure_job("UnitTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake db:migrate']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec:unit']))
stage = pipeline.ensure_stage("FunctionalTest")
job = stage.ensure_job("FunctionalTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec:functional']))

pipeline = configurator\
	.ensure_pipeline_group("pretend")\
	.ensure_replacement_of_pipeline("pretend_deals_service")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_deals_service")
pipeline.ensure_unencrypted_secure_environment_variables({"CF_EMAIL": CF_EMAIL, "CF_PASSWORD": CF_PASSWORD})
stage = pipeline.ensure_stage("Test")
job = stage.ensure_job("UnitTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec']))
stage = pipeline.ensure_stage("DeployStaging")
job = stage.ensure_job("Deploy")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake deploy_dev']))

pipeline = configurator\
	.ensure_pipeline_group("pretend")\
	.ensure_replacement_of_pipeline("pretend_web_app")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_web_app")
pipeline.ensure_unencrypted_secure_environment_variables({"CF_EMAIL": CF_EMAIL, "CF_PASSWORD": CF_PASSWORD})
stage = pipeline.ensure_stage("Test")
job = stage.ensure_job("UnitTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec']))
stage = pipeline.ensure_stage("DeployStaging")
job = stage.ensure_job("Deploy")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake deploy_dev']))

configurator.save_updated_config()
