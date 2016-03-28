#!/usr/bin/env python
from gomatic import *
import os

def _create_pipeline(group, pipeline_name, add_cf_vars=False):
	pipeline_group = configurator.ensure_pipeline_group(group)
	pipeline = pipeline_group.ensure_replacement_of_pipeline(pipeline_name)
	if(add_cf_vars == True):
		pipeline.ensure_unencrypted_secure_environment_variables({"CF_USERNAME": os.environ['CF_USERNAME'], "CF_PASSWORD": os.environ['CF_PASSWORD']})
		pipeline.ensure_environment_variables({"CF_HOME": "."})
	return pipeline

def _add_exec_task(job, command, working_dir=None, runif="passed"):
	job.add_task(ExecTask(['/bin/bash', '-l', '-c', command], working_dir=working_dir, runif=runif))

def _add_sudo_exec_task(job, command, working_dir=None, runif="passed"):
	job.add_task(ExecTask(['/bin/bash', '-c', 'sudo ' + command], working_dir=working_dir, runif=runif))

def build_csharp_pipeline_group(configurator):
	pipeline = _create_pipeline("csharp", "csharp_build")
	pipeline.set_git_url("https://github.com/wendyi/continuousSecurity")
	job = pipeline.ensure_stage("build").ensure_job("compile")
	_add_exec_task(job, 'rm -rf packages', 'csharp')
	_add_exec_task(job, '/home/vagrant/.dnx/runtimes/dnx-coreclr-linux-x64.1.0.0-rc1-update1/bin/dnu restore src/RecipeSharing', 'csharp')
	_add_exec_task(job, '/home/vagrant/.dnx/runtimes/dnx-coreclr-linux-x64.1.0.0-rc1-update1/bin/dnu build src/RecipeSharing', 'csharp')
	_add_exec_task(job, '/home/vagrant/.dnx/runtimes/dnx-coreclr-linux-x64.1.0.0-rc1-update1/bin/dnu restore test/RecipeSharing.UnitTests', 'csharp')
	_add_exec_task(job, '/home/vagrant/.dnx/runtimes/dnx-coreclr-linux-x64.1.0.0-rc1-update1/bin/dnu build test/RecipeSharing.UnitTests', 'csharp')
	job.ensure_artifacts({BuildArtifact("*", "csharp_build")})

	pipeline = _create_pipeline("csharp", "csharp_unit_test")
	pipeline.ensure_material(PipelineMaterial('csharp_build', 'build'))
	stage = pipeline.ensure_stage("unit_test")
	job = stage.ensure_job("run_tests")
	job = job.ensure_artifacts({TestArtifact("csharp_build/csharp/test/RecipeSharing.UnitTests")})
	job = job.ensure_tab(Tab("XUnit", "test/RecipeSharing.UnitTests/tests.txt"))
	job.add_task(FetchArtifactTask('csharp_build', 'build', 'compile', FetchArtifactDir('csharp_build')))
	_add_exec_task(job, '/home/vagrant/.dnx/runtimes/dnx-coreclr-linux-x64.1.0.0-rc1-update1/bin/dnx run > tests.txt', 'csharp_build/csharp/test/RecipeSharing.UnitTests')

def build_java_pipeline_group(configurator):
	pipeline = _create_pipeline("java", "java_build")
	pipeline.set_git_url("https://github.com/wendyi/continuousSecurity")
	job = pipeline.ensure_stage("build").ensure_job("compile")
	_add_exec_task(job, 'gradle --profile clean', 'java')
	_add_exec_task(job, 'gradle --profile compileJava', 'java')
	_add_exec_task(job, 'gradle --profile compileTestJava', 'java')
	job.ensure_artifacts({BuildArtifact("*", "java_build")})

	pipeline = _create_pipeline("java", "java_unit_test")
	pipeline.ensure_material(PipelineMaterial('java_build', 'build'))
	stage = pipeline.ensure_stage("unit_test")
	job = stage.ensure_job("run_tests")
	job = job.ensure_artifacts({TestArtifact("java_build/java/build/reports")})
	job = job.ensure_tab(Tab("JUnit", "reports/tests/index.html"))
	job.add_task(FetchArtifactTask('java_build', 'build', 'compile', FetchArtifactDir('java_build')))
	_add_exec_task(job, 'gradle --profile test', 'java_build/java')

def build_ruby_pipeline_group(configurator):
	pipeline = _create_pipeline("ruby", "ruby_build")
	pipeline.set_git_url("https://github.com/wendyi/continuousSecurity")
	job = pipeline.ensure_stage("build").ensure_job("bundle_install")
	_add_exec_task(job, 'bundle install --path vendor/bundle', 'ruby')
	job.ensure_artifacts({BuildArtifact("*", "ruby_build")})

	pipeline = _create_pipeline("ruby", "ruby_unit_test")
	pipeline.ensure_material(PipelineMaterial('ruby_build', 'build'))
	stage = pipeline.ensure_stage("unit_test")
	job = stage.ensure_job("run_tests")
	job = job.ensure_artifacts({TestArtifact("ruby_build/ruby/reports")})
	job = job.ensure_tab(Tab("RSpec", "reports/tests/index.html"))
	job.add_task(FetchArtifactTask('ruby_build', 'build', 'bundle_install', FetchArtifactDir('ruby_build')))
	_add_exec_task(job, 'bundle exec rake spec:unit', 'ruby_build/ruby')
	

def build_security_pipeline_group(configurator):
	pipeline = _create_pipeline("csharp_security", "csharp_vulnerable_components")
	pipeline.ensure_material(PipelineMaterial('csharp_build', 'build'))
	csharp_job = pipeline.ensure_stage("verify_components").ensure_job("check_csharp_dependencies")
	csharp_job.add_task(FetchArtifactTask('csharp_build', 'build', 'compile', FetchArtifactDir('csharp_build')))
	_add_sudo_exec_task(csharp_job, '/usr/local/bin/dependency-check/bin/dependency-check.sh --project "RecipeSharing" --scan "packages" --format ALL', 'csharp_build/csharp')
	_add_exec_task(csharp_job, 'grep "<li><i>Vulnerabilities Found</i>:&nbsp;0</li>" -c dependency-check-report.html', 'csharp_build/csharp')
	csharp_job = csharp_job.ensure_artifacts({TestArtifact("csharp_build/csharp/dependency-check-report.html")});
	csharp_job = csharp_job.ensure_tab(Tab("Vulnerabilities", "dependency-check-report.html"))

	pipeline = _create_pipeline("java_security", "java_vulnerable_components")
	pipeline.ensure_material(PipelineMaterial('java_build', 'build'))
	java_job1 = pipeline.ensure_stage("verify_components").ensure_job("check_java_dependencies")
	java_job1.add_task(FetchArtifactTask('java_build', 'build', 'compile', FetchArtifactDir('java_build')))
	_add_exec_task(java_job1, 'gradle --profile dependencyCheck', 'java_build/java')
	java_job1 = java_job1.ensure_artifacts({TestArtifact("java_build/java/build/reports/dependency-check-report.html")});
	java_job1 = java_job1.ensure_tab(Tab("Vulnerabilities", "dependency-check-report.html"))

	pipeline = _create_pipeline("java_security", "java_committed_secrets")
	pipeline.ensure_material(PipelineMaterial('java_build', 'build'))
	java_job2 = pipeline.ensure_stage("find_secrets").ensure_job("find_java_secrets")
	java_job2.add_task(FetchArtifactTask('java_build', 'build', 'compile', FetchArtifactDir('java_build')))
	_add_exec_task(java_job2, 'gradle --profile findSecrets', 'java_build/java')
	java_job2 = java_job2.ensure_artifacts({TestArtifact("java_build/java/build/reports/talisman.txt")});
	java_job2 = java_job2.ensure_tab(Tab("Secrets", "talisman.txt"))


	pipeline = _create_pipeline("ruby_security", "ruby_vulnerable_components")
	pipeline.ensure_material(PipelineMaterial('ruby_build', 'build'))
	ruby_job = pipeline.ensure_stage("verify_components").ensure_job("check_ruby_dependencies")
	ruby_job.add_task(FetchArtifactTask('ruby_build', 'build', 'bundle_install', FetchArtifactDir('ruby_build')))
	_add_exec_task(ruby_job, 'bundle exec rake dependency_check > vulnerabilities.txt', 'ruby_build/ruby')
	ruby_job = ruby_job.ensure_artifacts({TestArtifact("ruby_build/ruby/build/vulnerabilities.txt")});
	ruby_job = ruby_job.ensure_tab(Tab("Vulnerabilities", "vulnerabilities.txt"))

configurator = GoCdConfigurator(HostRestClient("localhost:8153"))
configurator.remove_all_pipeline_groups()
build_csharp_pipeline_group(configurator)
build_java_pipeline_group(configurator)
build_ruby_pipeline_group(configurator)
build_security_pipeline_group(configurator)
configurator.save_updated_config()
