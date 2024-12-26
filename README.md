# GoPro Plus Downloader

GoPro Plus is an open-source project designed to enable users to interact with
the GoPro Plus media library from the command line. This project aims to provide
a convenient way to access and manage your GoPro media without the need
to use the web interface.

**GoPro Plus supports downloading more than 25 media files at a time which is a
tedious 🤦 limitation enforced by GoPro Media Library website.**

 🐳 Docker hub: https://hub.docker.com/r/itsankoff/gopro

## Usage (Docker environment)
* `docker pull itsankoff/gopro`
* `docker run -e AUTH_TOKEN=<gopro-auth-token> -e USER_ID=<gopro-user-id> itsankoff/gopro:latest`.
    For `AUTH_TOKEN` and `USER_ID` check [Environment Variables](#environment-variables)

Supported Docker ENV variable options:

* `-e AUTH_TOKEN=<gopro-auth-token>` - (**required**) authentication token
        obtained from GoPro Media Library website. See [Environment Variables](#environment-variables).
* `-e USER_ID=<gopro-user-id>` - (**required**) user id
        obtained from GoPro Media Library website. See [Environment Variables](#environment-variables).
* `-e ACTION=<list|download>` - (*optional*) action to execute. The default is `download`.
* `-e START_PAGE=<number>` - (*optional*) run the `<action>` from specific page
        (GoPro Media Library API is paginated). The default `1`.
* `-e PAGES=<number>` - (*optional*) run the `<action>` over the specified number of pages.
        Default `1000000` which should mean max and will download the all cloud assets.
* `-e PER_PAGE=<number>` - (*optional*) specify number of items per page. Default `15`.
* `-e DOWNLOAD_PATH=<path>` - (*optional*) specify output path to download the assets.
        Default `./download` in current working directory.
* `-e PROGRESS_MODE=<inline|newline|noline>` - (*optional*) specify printing mode
        for download progress. Default `noline`.

## Environment Variables

To set up `AUTH_TOKEN` as an environment variable, you'll need to retrieve
your JWT token by logging into your GoPro Plus media library account.

1. Open a browser of choice (Firefox/Chrome is prefered, for Safari you need to enable Developer Tools)
2. Go to [GoPro Plus Media Library](https://plus.gopro.com/media-library/)  (assuming that you are signed out. If you are not, please sing out)
3. Open your browser's Developer Tools (Ctrl+Shift+I on most browsers or Cmd+Option+I on Mac).
4. Go to the Network Tab on the Developer Tools console.
5. In the Filter field enter - `user`
6. Open the request and find the Cookies tab in the Sub Preview. You need to find the two mandatory cookies:
    * `gp_access_token` - usually starts with `eyJhbGc...`. Copy this long sequence of gibberish characters into the env variable `AUTH_TOKEN`
    * `gp_user_id` - the user ID. Copy this ID into the env variable `USER_ID`

For Docker:
```bash
docker run -e AUTH_TOKEN=<gopro-auth-token> -e USER_ID=<gopro-user-id> itsankoff/gopro:latest
```

For Linux/macOS:
```bash
export AUTH_TOKEN="<gibberish_string_here>"
export USER_ID="<user-id>`
```

For Windows Command Prompt:
```cmd
set AUTH_TOKEN="<gibberish_string_here>"
set USER_ID="<user-id>"
```

For Windows PowerShell:
```sh
$env:AUTH_TOKEN="<gibberish_string_here>"
$env:USER_ID="<user-id>"
```

Once the `AUTH_TOKEN` and `USER_ID` is set, you can run the GoPro Plus application without needing to pass the token explicitly.
Remember to replace `<gibberish_string_here>` with the actual token you copied from the console.
By following these steps, you should be able to effectively manage your GoPro Plus media directly from your command line using GoPro Plus.


## Prerequisites (Local environment)

Before you can use GoPro Plus, you need to have the following installed:

* `python3.10+`
* `pip3`
* `direnv` (*optional*)
* `docker` (*optional*)


## Installation (Local environment)

To run GoPro Plus locally on your machine, follow these steps:

* `git clone https://github.com/itsankoff/gopro-plus.git`
* `cd gopro-plus`
* `python3 -m venv .venv`
* `pip3 install -r requirements.txt`
* (*optional*) `echo source .venv/bin/activate > .envrc # assuming direnv usage`
* (*optional*) `echo "export AUTH_TOKEN='<gopro-auth-token (see below)>'" >> .envrc # assuming direnv usage`


## Usage (Local environment)
* `./gopro` - running the help section

## Dev tooling
* `Makefile` - check for convenient shortcuts
    * `build` - build a docker container
    * `release` - build and release the docker image for multiple platforms.
    * `run` - run as local docker container
    * `stop` - stop docker container
    * `logs` - show docker logs in a follow mode
    * `clean` - stop and remove spawned containers

* `Dockerfile` - base configuration for the docker image
