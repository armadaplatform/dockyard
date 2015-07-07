import os
import sys
import subprocess

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../config'))
from config_json import get_config_json


environment = dict(os.environ)
environment['DOCKER_REGISTRY_CONFIG'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'registry-config.yml')

https_domain = get_config_json('HTTPS_DOMAIN')
read_only_registry = get_config_json('READ_ONLY')
if not https_domain and not read_only_registry:
    environment['REGISTRY_PORT'] = '80'


repository_path = get_config_json('REPOSITORY_PATH')
if repository_path and repository_path.startswith('s3:///'):
    environment['SETTINGS_FLAVOR'] = 's3'
    s3_path = repository_path[6:]
    s3_bucket, s3_directory = s3_path.split('/', 1)

    environment['AWS_S3_BUCKET'] = s3_bucket
    if s3_directory:
        environment['STORAGE_PATH'] = s3_directory

    for key in ('AWS_ACCESS_KEY', 'AWS_ACCESS_SECRET', 'S3_ENCRYPT', 'S3_USE_HTTPS'):
        value = get_config_json(key)
        if value:
            environment[key] = value

else:
    environment['SETTINGS_FLAVOR'] = 'local'
    if repository_path:
        environment['STORAGE_PATH'] = repository_path

subprocess.Popen(['docker-registry'], env = environment)
