# GoPro Plus

GoPro Plus is an open-source project designed to enable users to interact with
the GoPro Plus media library from the command line. This project aims to provide
a convenient way to access and manage your GoPro media without the need
to use the web interface.

**GoPro Plus supports downloading more than 25 media files at a time which is a
tedious 🤦 limitation enforced by GoPro Media Library website.**


## Usage (Docker environment)
* `docker pull itsankoff/gopro`
* `docker run -e AUTH_TOKEN=<gopro-auth_token> itsankoff/gopro`

Supported Docker ENV variable options:
* `-e AUTH_TOKEN=<gopro-auth-token>` - (**required**) authentication token
        obtained from GoPro Media Library website. See [setup guide](#setting-up-auth_token-as-environment-variable).
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
