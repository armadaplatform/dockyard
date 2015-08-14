# dockyard

`dockyard` service contains armadized [docker registry](https://github.com/docker/docker-registry) - a place to store
your docker container images.
It is accompanied by nginx server which allows adding authentication layer and connection encryption with SSL.

Currently it still uses the "old" (python) registry implementation.
Switch to ["Docker registry 2.0"](https://docs.docker.com/registry/) is planned.


# Building the service.

    armada build dockyard


# Running the service.

## Choosing storage.

The service supports two storage options:

1. Registry stored in filesystem.

    Registry is stored in directory `/repository` inside the container.
    To ensure persistent storage it should be mapped to some folder on the host machine,
    e.g. `/var/opt/dockyard.initech.com`:

        armada run dockyard -v /var/opt/dockyard.initech.com:/repository


2. Registry stored in AWS S3.

    You have to provide S3 bucket path with suitable access and secret keys:

        armada run dockyard -e "REPOSITORY_PATH=s3:///com-initech-dockyard/" "AWS_ACCESS_KEY=..." "AWS_ACCESS_SECRET=..."

    Beware not to use dot character in your bucket name (e.g. `com.initech.dockyard`). Amazon's S3 SSL certificate
    is valid only for first-level subdomains of `s3.amazonaws.com` through which API calls are made.
    Requests to `https://com.initech.dockyard.s3.amazonaws.com` would be invalid and the dockyard wouldn't work.


## Securing dockyard.

### HTTPS.

Dockyard can be run either behind HTTP or HTTPS protocols.
The first option may be convenient for local development registry, but in production environments HTTPS should be used.
To run dockyard that way we have to provide correct SSL certificate.
Assuming we have proper keys in `/etc/ssl/dockyard.initech.com` directory we can run:

    armada run dockyard ... -v /etc/ssl/dockyard.initech.com:/ssl_keys -e "HTTPS_DOMAIN=dockyard.initech.com" "SSL_CRT_FILE=/ssl_keys/dockyard.initech.com.crt" "SSL_KEY_FILE=/ssl_keys/dockyard.initech.com.key"


### Basic HTTP authentication.

When using HTTPS, we can also add basic HTTP authentication, so that only users knowing proper credentials can access it.
In addition to other parameters we can run:

    armada run dockyard ... -e "HTTP_AUTH_USER=admin" "HTTP_AUTH_PASSWORD=secret!"

This type of authentication can only be used with dockyard with HTTPS configured.


### Read only mode.

If you want to run dockyard in read only mode you can add parameter `READ_ONLY`:

    armada run dockyard ... -e "READ_ONLY=1"

It can be useful to have 2 dockyards running. One with authenticated read/write access for the developers, and the other
read only one for your customers.


## Hermes.

All of the above configuration options can also be supplied by Hermes, so that you don't have to type them all the time.
The configuration should be stored in file `config.json` that contains single json object.
Its key/value pairs correspond to the explained environment variables.
E.g.:

    {
        "REPOSITORY_PATH": "s3:///com-initech-dockyard/",
        "AWS_ACCESS_KEY": "xxx",
        "AWS_ACCESS_SECRET": "xxx",

        "HTTPS_DOMAIN": "dockyard.initech.com",
        "SSL_CRT_FILE": "ssl_keys/dockyard.initech.com.crt",
        "SSL_KEY_FILE": "ssl_keys/dockyard.initech.com.key",

        "READ_ONLY": true
    }

SSL certificate files should also be provided by Hermes. Path to them (`SSL_CRT_FILE`, `SSL_KEY_FILE`) is relative to
`config.json` file.
