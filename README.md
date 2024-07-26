# GoPro Plus

GoPro Plus is an open-source project designed to enable users to interact with
the GoPro Plus media library from the command line. This project aims to provide
a convenient way to access and manage your GoPro media without the need
to use the web interface.

**GoPro Plus supports downloading more than 25 media files at a time which is a
tedious 🤦 limitation enforced by GoPro Media Library website.**

 🐳 Docker hub: https://hub.docker.com/repository/docker/itsankoff/gopro/general

## Usage (Docker environment)
* `docker pull itsankoff/gopro`
* `docker run -e AUTH_TOKEN=<gopro-auth_token> --mount type=bind,src="`pwd`/download",target=/app/download itsankoff/gopro`

Supported Docker ENV variable options:
* `-e AUTH_TOKEN=<gopro-auth-token>` - (**required**) authentication token
        obtained from GoPro Media Library website. See [setup guide](#setting-up-auth_token-as-environment-variable).
* `-e ACTION=<list|download|download-upload>` - (*optional*) action to execute. The default is `download`.
* `-e START_PAGE=<number>` - (*optional*) run the `<action>` from specific page
        (GoPro Media Library API is paginated). The default `1`.
* `-e PAGES=<number>` - (*optional*) run the `<action>` over the specified number of pages.
        Default `1000000` which should mean max and will download the all cloud assets.
* `-e PER_PAGE=<number>` - (*optional*) specify number of items per page. Default `15`.
* `-e DOWNLOAD_PATH=<path>` - (*optional*) specify output path to download the assets.
        Default `./download` in current working directory.
* `-e PROGRESS_MODE=<inline|newline|noline>` - (*optional*) specify printing mode
        for download progress. Default `noline`.
* `-e S3_ENDPOINT_URL=<s3 endpoint url>` - (*optional*) specify the S3 endpoint URL for S3 upload.
        Default `s3.us-west-2.amazonaws.com`
* `-e S3_BUCKET_NAME=<s3 bucket name>` - (*optional*) specify the S3 bucket name for S3 upload.
* `-e AWS_ACCESS_KEY_ID=<aws access key id>` - (*optional*) specify the AWS_ACCESS_KEY_ID for S3 upload.
* `-e AWS_SECRET_ACCESS_KEY=<aws secret access key>` - (*optional*) specify the AWS_SECRET_ACCESS_KEY for S3 upload.

## Prerequisites (Local environment)

Before you can use GoPro Plus, you need to have the following installed:

* `python3.10+`
* `pip3`
* `virtualenv`
* `direnv` (*optional*)
* `docker` (*optional*)


## Installation (Local environment)

To run GoPro Plus locally on your machine, follow these steps:

* `git clone https://github.com/itsankoff/gopro-plus.git`
* `cd gopro-plus`
* `virtualenv .venv`
* (*optional*) `echo source .venv/bin/activate > .envrc # assuming direnv usage`
* (*optional*) `echo AUTH_TOKEN="<gopro-auth-token (see below)>" >> .envrc # assuming direnv usage`


## Usage (Local environment)
* `./gopro` - running the help section

## Dev tooling
* `Makefile` - check for convenient shortcuts
    * `build` - build a docker container
    * `run` - run as local docker container
    * `release` - building the docker image for multiple platforms.
    * `stop` - stop docker container
    * `logs` - show docker logs in a follow mode
    * `clean` - stop and remove spawned containers

* `Dockerfile` - base configuration for the docker image

## Setting Up AUTH_TOKEN as Environment Variable

To set up `AUTH_TOKEN` as an environment variable, you'll need to retrieve
your JWT token by logging into your GoPro Plus media library account.

1. Open a browser of choice (Firefox/Chrome is prefered, for Safari you need to enable Developer Tools)
2. Go to [GoPro Plus Media Library](https://plus.gopro.com/media-library/)  (assuming that you are signed out. If you are not, please sing out)
3. Open your browser's Developer Tools (Ctrl+Shift+I on most browsers or Cmd+Option+I on Mac).
4. Go to the Network Tab on the Developer Tools console.
5. In the Filter field enter - `server-io`
6. In the `Headers` tab, look for Cookies header and find in its content `gp_access_token`.
    It should starts with `eyJhbG...`.
7. Copy the string (it should be a long sequence of gibberish characters)

For Linux/macOS:
```sh
export AUTH_TOKEN="<gibberish_string_here>"
```

For Windows Command Prompt:
```cmd
set AUTH_TOKEN="<gibberish_string_here>"
```

For Windows PowerShell:
```sh
$env:AUTH_TOKEN="<gibberish_string_here>"
```

Once the AUTH_TOKEN is set, you can run the GoPro Plus application without needing to pass the token explicitly.
Remember to replace `<gibberish_string_here>` with the actual token you copied from the console.
By following these steps, you should be able to effectively manage your GoPro Plus media directly from your command line using GoPro Plus.

## S3 upload
When setting `action=download-upload`, the app will upload the files to S3 immediately and delete the local file after upload completes.  

You will need to provide additional environment variables for AWS credentials and S3.  

```
export S3_ENDPOINT_URL="s3.us-west-2.amazonaws.com"
export AWS_ACCESS_KEY_ID="xxxxxxxxx"
export AWS_SECRET_ACCESS_KEY="xxxxxxxxxxxxxxxxx"
export S3_BUCKET_NAME="MyS3Bucket"
```