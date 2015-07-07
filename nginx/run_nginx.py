from __future__ import print_function
import os
import sys
import subprocess
import htpasswd

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../config'))
from config_json import get_config_json


NGINX_CONFIG_PATH = '/etc/nginx/sites-available/dockyard'
HTPASSWD_PATH = '/etc/nginx/registry.htpasswd'

https_domain = get_config_json('HTTPS_DOMAIN')
ssl_crt_file = get_config_json('SSL_CRT_FILE', return_path = True)
ssl_key_file = get_config_json('SSL_KEY_FILE', return_path = True)
http_auth_user = get_config_json('HTTP_AUTH_USER')
http_auth_password = get_config_json('HTTP_AUTH_PASSWORD')
read_only_registry = get_config_json('READ_ONLY')

def parse_config_template(config_template_path, config_variables, config_output_path):

    with open(config_template_path, 'r') as config_file:
        nginx_config = config_file.read()

    for k, v in config_variables.iteritems():
        nginx_config = nginx_config.replace(k, v)

    with open(config_output_path, 'w') as config_file:
        config_file.write(nginx_config)

#===================================================================================================

if not https_domain and not read_only_registry:
    print("No HTTPS domain configured and not read only registry. Theres is no need to run nginx.")
    sys.exit(0)

config_template_path = 'nginx-http.config'
nginx_config_variables = { '<READ_ONLY>': '1' if read_only_registry else '0' }

if https_domain:
    if (not ssl_crt_file or not os.path.isfile(ssl_crt_file) or
        not ssl_key_file or not os.path.isfile(ssl_key_file)):
        print("ERROR: SSL certificate files not found.")
        sys.exit(1)
    # Protect SSL certificate files in case nginx/registry is compromised.
    os.system('chmod 600 {0} {1}'.format(ssl_crt_file, ssl_key_file))

    config_template_path = 'nginx-https.config'
    nginx_config_variables['<HTTPS_DOMAIN>'] = https_domain
    nginx_config_variables['<SSL_CRT_FILE_PATH>'] = ssl_crt_file
    nginx_config_variables['<SSL_KEY_FILE_PATH>'] = ssl_key_file

    if http_auth_user and http_auth_password:
        config_template_path = 'nginx-https-auth.config'

        with open(HTPASSWD_PATH, 'w'):
            pass
        with htpasswd.Basic(HTPASSWD_PATH) as userdb:
            try:
                userdb.add(http_auth_user, http_auth_password)
            except htpasswd.basic.UserExists, e:
                print(e)

        nginx_config_variables['<HTPASSWD_FILE_PATH>'] = HTPASSWD_PATH


#===================================================================================================


parse_config_template(config_template_path, nginx_config_variables, NGINX_CONFIG_PATH)
try:
    os.symlink(NGINX_CONFIG_PATH, '/etc/nginx/sites-enabled/dockyard')
except:
    pass

subprocess.Popen('service nginx start'.split())
