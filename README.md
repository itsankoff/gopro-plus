# GoPro Plus

GoPro Plus is an open-source project designed to enable users to interact with
the GoPro Plus media library from the command line. This project aims to provide
a convenient way to access and manage your GoPro media without the need
to use the web interface.

Also, it supports downloading more than 25 media files at a time which is a
tedious limitation enforced by GoPro Media Library website.

## Prerequisites

Before you can use GoPro Plus, you need to have the following installed:

* `python3.10+`
* `pip3`
* `virtualenv`
* `direnv` optional
* `docker` optional

## Installation (Local development)

To run GoPro Plus locally on your machine, follow these steps:

* `git clone https://github.com/itsankoff/gopro-plus.git`
* `cd gopro-plus`
* `virtualenv .venv`
* `echo source .venv/bin/activate > .envrc # assuming direnv usage`
* `echo AUTH_TOKEN="<gopro-auth-token (see below)>" >> .envrc # assuming direnv usage`


## Usage (Local environment)
* `./gopro` - running the help section

## Usage (Docker environment)
* `docker pull itsankoff/gopro`
* `docker run -e AUTH_TOKEN=<gopro-auth_token> itsankoff/gopro`


## Setting Up AUTH_TOKEN as Environment Variable

To set up AUTH_TOKEN as an environment variable, you'll need to retrieve your JWT token by logging into your GoPro Plus media library account.

1. Go to GoPro Plus Media Library.
2. Log in with your GoPro credentials.
3. Once logged in, open your browser's Developer Tools (Ctrl+Shift+I on most browsers or Cmd+Option+I on Mac).
4. Click on the Console tab.
5. Type localStorage.getItem('auth_token') and press Enter.
6. Copy the token that is displayed.
7. Now, you can set the AUTH_TOKEN environment variable in your shell:

For Linux/macOS:
```sh
export AUTH_TOKEN='your_copied_token_here'
```

For Windows Command Prompt:
```cmd
set AUTH_TOKEN=your_copied_token_here
```

For Windows PowerShell:
```ps
$env:AUTH_TOKEN="your_copied_token_here"
```

Once the AUTH_TOKEN is set, you can run the GoPro Plus application without needing to pass the token explicitly.

Remember to replace 'your_copied_token_here' with the actual token you copied from the console.

By following these steps, you should be able to effectively manage your GoPro Plus media directly from your command line using GoPro Plus.
