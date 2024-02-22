# CI Machines tunnel

**DISCLAIMER**: If you're not working at the same company as I am, this project might not be relevant to you. Though, you can fork to make few adjustments to make it relevant.

This simple flask app writen in Python is a simple web application to tunnel (using ngrok) the CI machines websites using a machine that's connected to the company VPN. It's an easy way to look at the summary of all machines without going through one by one, but still limits the informations and actions given, so that the user will still need to access the original pages if necessary.

## Usage

Before running, please make sure Python 3 is installed, and then install all required modules by running `pip install -r requirements.txt`.

You can run manually the application by running this command from the root directory:
- `flask run`, or
- `python -m flask run`

To enable the tunnel using ngrok, follow the step in [ngrok official documentation](https://ngrok.com/docs/), to tunnel the default flask app port (5000).

To alter the list of the monitored CI machines, open `modules/server.py` file and make the necessary adjustment to the `CIs` variable. It's currently containing the CI machines monitored by my team.

## Docker

To run the application inside docker, take a look at `dockerfile` and `docker-compose.yml` files and make the necessary changes:
- If you want to change the default port (eg. to 3000), there are 2 simple ways:
    1. change the `CMD` in `dockerfile` to add `--port` and `3000` to the arguments. Next, open `docker-compose.yml` change the `ports` for the `flask-app` service and `command` for the `ngrok` service to the appropriate port. Or,
    2. you can simply open `docker-compose.yml` file and change the exposed port for the `flask-app` service to `"3000:5000"`, and adjust the `command` for the `ngrok` service as such.
- This part is necessary, you need to provide you ngrok authtoken, by replace the `<YOUR-NGROK-AUTHTOKEN>` in `environment` for the `ngrok` service inside `docker-compose.yml` with your ngrok authtoken.
- If you want to use a static domain, replace `<YOUR-STATIC-DOMAIN>` in `command` for the `ngrok` service as well. If not, you can omit the `--domain` altogether.