"""define app entry point"""
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.requests import Request
from starlette.background import BackgroundTask
from secretkey import key
import logging
import hmac
import subprocess
import os
import yaml
import sys

logging.basicConfig(format='%(asctime)s - %(message)s', filename='output.log', level=logging.INFO)

app = Starlette(debug=True)

@app.on_event('startup')
def startup():
    logging.info('application startup')

@app.on_event('shutdown')
def shutdown():
    logging.critical('application shutdown')

async def hook(scope, receive, send):
    assert scope['type'] == 'http'
    request = Request(scope, receive)
    sig = hmac.new(key, digestmod='sha1')
    body = await request.body()
    sig.update(body)
    valid = 'X-Hub-Signature' in request.headers and hmac.compare_digest(
        'sha1={}'.format(sig.hexdigest()),
        request.headers['X-Hub-Signature']
    )
    response = PlainTextResponse(
        str(valid),
        background=BackgroundTask(
            rebuild_deploy,
            body=await request.json()
        ) if valid else None
    )
    await response(scope, receive, send)


def cd(path):
    os.chdir(os.path.expanduser(path))

def run_cmd(args):
    return subprocess.run(
        args,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

def parse_compose(fr, build_dir):
    if not isinstance(fr, dict):
        return False
    if 'build' in fr and build_dir in fr['build']:
        return True
    for key in fr:
        if parse_compose(fr[key], build_dir):
            return True
    return False

def rebuild_deploy(body):
    project = body['repository']['name']
    clone = body['repository']['clone_url']
    try:
        os.mkdir(os.path.expanduser('~/projects'))
    except FileExistsError:
        logging.critical('projects folder already exists')
        pass
    cd('~/projects')
    if not os.path.exists(project):
        logging.critical(run_cmd(['git', 'clone', clone]))
    else:
        cd(project)
        logging.info(run_cmd(['git', 'reset', '--hard']).stdout)
        logging.info(run_cmd(['git', 'pull']).stdout)
        logging.info(run_cmd(['git', 'lfs', 'pull']).stdout)
    if os.path.isfile(os.path.expanduser('~/docker-compose.yml')):
        logging.critical('attempting to rebuild image')
        cd('~')
        with open('docker-compose.yml', 'r') as stream:
            try:
                file = yaml.safe_load(stream)
                if parse_compose(file, project):
                    logging.critical('issuing docker rebuild')
                    logging.info(run_cmd(['docker-compose', 'up', '-d', '--build']).stdout)
                else:
                    logging.critical('no matching image found in docker-compose.yml')
            except yaml.YAMLError as e:
                logging.critical(e)
                logging.critical('could not read docker-compose.yml')

app.mount('/hook', hook)