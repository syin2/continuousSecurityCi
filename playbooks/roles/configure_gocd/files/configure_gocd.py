#!/usr/bin/env python
from gomatic import *
import os

def _create_pipeline(group, pipeline_name, add_cf_vars=False):
	pipeline_group = configurator.ensure_pipeline_group(group)
	pipeline = pipeline_group.ensure_replacement_of_pipeline(pipeline_name)
	if(add_cf_vars == True):
		pipeline.ensure_unencrypted_secure_environment_variables({"CF_EMAIL": os.environ['CF_EMAIL'], "CF_PASSWORD": os.environ['CF_PASSWORD'], "CF_HOME": "."})
	return pipeline

def _add_exec_task(job, command, working_dir=None, runif="passed"):
	job.add_task(ExecTask(['/bin/bash', '-l', '-c', command], working_dir=working_dir, runif=runif))

def build_catalog_pipeline_group(configurator):
	pipeline = _create_pipeline("catalog", "catalog_unit_tests")
	pipeline.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_catalog_service")
	job = pipeline.ensure_stage("test").ensure_job("test")
	_add_exec_task(job, 'bundle install --path vendor/bundle --without production')
	_add_exec_task(job, 'bundle exec rake spec:unit')
	job.ensure_artifacts({TestArtifact("spec/reports")})
	job.ensure_artifacts({BuildArtifact("*", "catalog_build")})

	pipeline = _create_pipeline("catalog", "catalog_functional_tests", True)
	pipeline.ensure_material(PipelineMaterial('catalog_unit_tests', 'test'))
	job = pipeline.ensure_stage("test").ensure_job("test")
	job.add_task(FetchArtifactTask('catalog_unit_tests', 'test', 'test', FetchArtifactDir('catalog_build')))
	_add_exec_task(job, 'bundle exec rake deploy_dev', 'catalog_build')

def build_pricing_pipeline_group(configurator):
	pipeline = _create_pipeline("pricing", "pricing_unit_tests")
	pipeline.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_pricing_service")
	job = pipeline.ensure_stage("test").ensure_job("test")
	_add_exec_task(job, 'bundle install --path vendor/bundle')
	_add_exec_task(job, 'bundle exec rake db:migrate')
	_add_exec_task(job, 'bundle exec rake spec:unit')
	job.ensure_artifacts({TestArtifact("spec/reports")})
	job.ensure_artifacts({BuildArtifact("*", "pricing_build")})

	pipeline = _create_pipeline("pricing", "pricing_functional_tests", True)
	pipeline.ensure_material(PipelineMaterial('pricing_unit_tests', 'test'))
	job = pipeline.ensure_stage("test").ensure_job("test")
	job.add_task(FetchArtifactTask('pricing_unit_tests', 'test', 'test', FetchArtifactDir('pricing_build')))
	_add_exec_task(job, 'APP_NAME=pricing_$GO_PIPELINE_NAME$GO_PIPELINE_COUNTER bundle exec rake spec:functional', 'pricing_build')
	job.ensure_artifacts({TestArtifact("spec/reports")})

def build_deals_pipeline_group(configurator):
	pipeline = _create_pipeline("deals", "deals_unit_tests")
	pipeline.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_deals_service")
	job = pipeline.ensure_stage("test").ensure_job("test")
	_add_exec_task(job, 'bundle install --path vendor/bundle --without production')
	_add_exec_task(job, 'bundle exec rake spec:unit')
	job.ensure_artifacts({TestArtifact("spec/reports")})
	job.ensure_artifacts({BuildArtifact("*", "deals_build")})

	pipeline = _create_pipeline("deals", "deals_functional_tests", True)
	pipeline.ensure_material(PipelineMaterial('pricing_unit_tests', 'test'))
	pipeline.ensure_material(PipelineMaterial('deals_unit_tests', 'test'))
	job = pipeline.ensure_stage("test").ensure_job("test")
	job.add_task(FetchArtifactTask('pricing_unit_tests', 'test', 'test', FetchArtifactDir('pricing_build')))
	job.add_task(FetchArtifactTask('deals_unit_tests', 'test', 'test', FetchArtifactDir('deals_build')))
	_add_exec_task(job, 'bundle exec rake app:deploy[test,pricing_$GO_PIPELINE_NAME$GO_PIPELINE_COUNTER,pricing_$GO_PIPELINE_NAME$GO_PIPELINE_COUNTER]', 'pricing_build')
	_add_exec_task(job, 'PRICING_SERVICE_URL=http://pricing_$GO_PIPELINE_NAME$GO_PIPELINE_COUNTER.cfapps.io APP_NAME=deals_$GO_PIPELINE_NAME$GO_PIPELINE_COUNTER bundle exec rake spec:functional', 'deals_build')
	_add_exec_task(job, 'bundle exec rake app:delete[test,pricing_$GO_PIPELINE_NAME$GO_PIPELINE_COUNTER]', 'pricing_build', "any")
	job.ensure_artifacts({TestArtifact("spec/reports")})

def build_web_app_pipeline_group(configurator):
	pipeline = _create_pipeline("web_app", "pretend_web_app", True)
	pipeline.set_git_url("https://github.com/ThoughtWorks-AELab/pretend_web_app")
	job = pipeline.ensure_stage("test").ensure_job("test")
	_add_exec_task(job, 'bundle install --path vendor/bundle --without production')
	_add_exec_task(job, 'bundle exec rake spec:unit')
	job.ensure_artifacts({TestArtifact("spec/reports")})

	job = pipeline.ensure_stage("DeployStaging").ensure_job("Deploy")
	_add_exec_task(job, 'bundle install --path vendor/bundle --without production')
	_add_exec_task(job, 'bundle exec rake deploy_dev')

configurator = GoCdConfigurator(HostRestClient("localhost:8153"))
build_catalog_pipeline_group(configurator)
build_pricing_pipeline_group(configurator)
build_deals_pipeline_group(configurator)
build_web_app_pipeline_group(configurator)
configurator.save_updated_config()
