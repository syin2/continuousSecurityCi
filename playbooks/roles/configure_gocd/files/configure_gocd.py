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

def build_source_pipeline_group(configurator):
	pipeline = _create_pipeline("source", "checkout")
	pipeline.set_git_url("https://github.com/wendyi/continuousSecurity")
	checkout_job = pipeline.ensure_stage("source").ensure_job("checkout")
	checkout_job.ensure_artifacts({BuildArtifact("*", "source")})

def build_csharp_pipeline_group(configurator):
	pipeline = _create_pipeline("csharp", "csharp_build")
	pipeline.set_git_url("https://github.com/wendyi/continuousSecurityCsharp")
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

	pipeline = _create_pipeline("csharp", "csharp_vulnerable_components")
	pipeline.ensure_material(PipelineMaterial('csharp_build', 'build'))
	csharp_job = pipeline.ensure_stage("verify_components").ensure_job("check_csharp_dependencies")
	csharp_job.add_task(FetchArtifactTask('csharp_build', 'build', 'compile', FetchArtifactDir('csharp_build')))
	_add_sudo_exec_task(csharp_job, '/usr/local/bin/dependency-check/bin/dependency-check.sh --project "RecipeSharing" --scan "packages" --format ALL', 'csharp_build/csharp')
	_add_exec_task(csharp_job, 'grep "<li><i>Vulnerabilities Found</i>:&nbsp;0</li>" -c dependency-check-report.html', 'csharp_build/csharp')
	csharp_job = csharp_job.ensure_artifacts({TestArtifact("csharp_build/csharp/dependency-check-report.html")});
	csharp_job = csharp_job.ensure_tab(Tab("Vulnerabilities", "dependency-check-report.html"))


def build_java_pipeline_group(configurator):
	pipeline = _create_pipeline("java", "java_secrets")
	pipeline.set_git_url("https://github.com/wendyi/continuousSecurityJava")
	secrets_job = pipeline.ensure_stage("java_secrets_stage") \
		.ensure_job("find_secrets_job") \
		.ensure_artifacts({BuildArtifact("*", "find_secrets_job")}) \
		.ensure_artifacts({TestArtifact("java/build/reports")}) \
		.ensure_tab(Tab("Secrets", "talisman.txt")) 
	_add_exec_task(secrets_job, 'gradle --profile findSecrets --debug', 'java')

	pipeline = _create_pipeline("java", "java_build")
	pipeline.ensure_material(PipelineMaterial('java_secrets', 'java_secrets_stage'))
	compile_job = pipeline.ensure_stage("java_build_stage") \
		.ensure_job("java_compile_job") \
		.ensure_artifacts({BuildArtifact("*", "java_compile_job")})
	compile_job.add_task(FetchArtifactTask('java_secrets', 'java_secrets_stage', 'find_secrets_job', FetchArtifactDir('find_secrets_job/java')))
	_add_exec_task(compile_job, 'gradle --profile clean', 'java')
	_add_exec_task(compile_job, 'gradle --profile compileJava', 'java')
	_add_exec_task(compile_job, 'gradle --profile compileTestJava', 'java')

	pipeline = _create_pipeline("java", "java_unit_test")
	pipeline.ensure_material(PipelineMaterial('java_build', 'java_build_stage'))
	unit_test_job = pipeline.ensure_stage("unit_test") \
		.ensure_job("run_tests") \
		.ensure_artifacts({TestArtifact("java_build/java/build/reports")}) \
		.ensure_tab(Tab("JUnit", "reports/tests/index.html"))
	unit_test_job.add_task(FetchArtifactTask('java_build', 'java_build_stage', 'java_compile_job', FetchArtifactDir('java_compile_job/java')))
	_add_exec_task(unit_test_job, 'gradle --profile test', 'java')

	pipeline = _create_pipeline("java", "java_vulnerable_components")
	pipeline.ensure_material(PipelineMaterial('java_build', 'java_build_stage'))
	vulnerable_components_job = pipeline.ensure_stage("verify_components") \
		.ensure_job("check_java_dependencies") \
		.ensure_artifacts({TestArtifact("java/build/reports/dependency-check-report.html")}) \
		.ensure_tab(Tab("Vulnerabilities", "dependency-check-report.html"))
	vulnerable_components_job.add_task(FetchArtifactTask('java_build', 'java_build_stage', 'java_compile_job', FetchArtifactDir('java_compile_job/java')))
	_add_exec_task(vulnerable_components_job, 'gradle --profile dependencyCheck', 'java')

def build_ruby_pipeline_group(configurator):
	pipeline = _create_pipeline("ruby", "ruby_build")
	pipeline.set_git_url("https://github.com/wendyi/continuousSecurityRuby")
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

	pipeline = _create_pipeline("ruby_security", "ruby_vulnerable_components")
	pipeline.ensure_material(PipelineMaterial('ruby_build', 'build'))
	ruby_job = pipeline.ensure_stage("verify_components").ensure_job("check_ruby_dependencies")
	ruby_job.add_task(FetchArtifactTask('ruby_build', 'build', 'bundle_install', FetchArtifactDir('ruby_build')))
	_add_exec_task(ruby_job, 'bundle exec rake dependency_check > vulnerabilities.txt', 'ruby_build/ruby')
	ruby_job = ruby_job.ensure_artifacts({TestArtifact("ruby_build/ruby/build/vulnerabilities.txt")});
	ruby_job = ruby_job.ensure_tab(Tab("Vulnerabilities", "vulnerabilities.txt"))

configurator = GoCdConfigurator(HostRestClient("localhost:8153"))
configurator.remove_all_pipeline_groups()
build_source_pipeline_group(configurator)
build_csharp_pipeline_group(configurator)
build_java_pipeline_group(configurator)
build_ruby_pipeline_group(configurator)
build_security_pipeline_group(configurator)
configurator.save_updated_config()
