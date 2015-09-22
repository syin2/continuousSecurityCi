#!/usr/bin/env python
from gomatic import *
import os

CF_EMAIL = os.environ['CF_EMAIL']
CF_PASSWORD = os.environ['CF_PASSWORD']

configurator = GoCdConfigurator(HostRestClient("localhost:8153"))

pipeline_group = configurator.ensure_pipeline_group("catalog")
	
pipeline = pipeline_group\
  .ensure_replacement_of_pipeline("catalog_unit_tests")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_catalog_service")
stage = pipeline.ensure_stage("Test")
job = stage.ensure_job("UnitTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec:unit']))
job.ensure_artifacts({TestArtifact("spec/reports")})
job.ensure_artifacts({BuildArtifact("*", "build")})

pipeline = pipeline_group\
    .ensure_replacement_of_pipeline("catalog_functional_tests")\
    .ensure_material(PipelineMaterial('catalog_unit_tests', 'Test'))
pipeline.ensure_unencrypted_secure_environment_variables({"CF_EMAIL": CF_EMAIL, "CF_PASSWORD": CF_PASSWORD})
stage = pipeline.ensure_stage("DeployStaging")
job = stage.ensure_job("Deploy")
job.add_task(FetchArtifactTask('catalog_unit_tests', 'Test', 'UnitTest', FetchArtifactDir('build')))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake deploy_dev'], 'build'))

pipeline_group = configurator.ensure_pipeline_group("deals")
pipeline = pipeline_group\
	.ensure_replacement_of_pipeline("pretend_deals_service")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_deals_service")
pipeline.ensure_unencrypted_secure_environment_variables({"CF_EMAIL": CF_EMAIL, "CF_PASSWORD": CF_PASSWORD})
stage = pipeline.ensure_stage("Test")
job = stage.ensure_job("UnitTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec:unit']))
job.ensure_artifacts({TestArtifact("spec/reports")})

stage = pipeline.ensure_stage("DeployStaging")
job = stage.ensure_job("Deploy")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake deploy_dev']))

pipeline_group = configurator.ensure_pipeline_group("pricing")
pipeline = pipeline_group\
	.ensure_replacement_of_pipeline("pricing_unit_tests")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_pricing_service")
stage = pipeline.ensure_stage("UnitTest")
job = stage.ensure_job("UnitTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake db:migrate']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec:unit']))
job.ensure_artifacts({TestArtifact("spec/reports")})

pipeline = pipeline_group\
    .ensure_replacement_of_pipeline("pricing_functional_tests")\
    .ensure_material(PipelineMaterial('pricing_unit_tests', 'UnitTest'))
pipeline.ensure_unencrypted_secure_environment_variables({"CF_EMAIL": CF_EMAIL, "CF_PASSWORD": CF_PASSWORD})
stage = pipeline.ensure_stage("FunctionalTest")
job = stage.ensure_job("FunctionalTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec:functional']))
job.ensure_artifacts({TestArtifact("spec/reports")})

pipeline_group = configurator.ensure_pipeline_group("web_app")
pipeline = pipeline_group\
	.ensure_replacement_of_pipeline("pretend_web_app")\
	.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_web_app")
pipeline.ensure_unencrypted_secure_environment_variables({"CF_EMAIL": CF_EMAIL, "CF_PASSWORD": CF_PASSWORD})
stage = pipeline.ensure_stage("Test")
job = stage.ensure_job("UnitTest")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake spec:unit']))
job.ensure_artifacts({TestArtifact("spec/reports")})
stage = pipeline.ensure_stage("DeployStaging")
job = stage.ensure_job("Deploy")
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle install --path vendor/bundle --without production']))
job.add_task(ExecTask(['/bin/bash', '-l', '-c', 'bundle exec rake deploy_dev']))

configurator.save_updated_config()
