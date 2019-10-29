"""define app entry point"""
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.requests import Request
from starlette.background import BackgroundTask
from secretkey import key
import logging
import hmac
import os


app = Starlette(debug=True)

async def hook(scope, receive, send):
    assert scope['type'] == 'http'
    request = Request(scope, receive)
    sig = hmac.new(key, digestmod='sha1')
    body = await request.body()
    sig.update(body)
    assert hmac.compare_digest(
        'sha1={}'.format(sig.hexdigest()),
        request.headers['X-Hub-Signature']
    )
    body_json = await request.json()
    task = BackgroundTask(
        rebuild_deploy,
        body=body_json
    )
    response = PlainTextResponse('success', background=task)
    await response(scope, receive, send)


def cd(path):
    os.chdir(os.path.expanduser(path))


def rebuild_deploy(body):
    project = body['repository']['name']
    clone = body['repository']['clone_url']
    try:
        os.mkdir(os.path.expanduser('~/projects'))
    except FileExistsError:
        logging.critical('projects folder already exists')
        pass
    cd('~/projects')
    clone_string = 'git clone {}'.format(clone)
    logging.critical(clone_string)
    code = os.system(clone_string)
    logging.critical(code)
    if code:
        cd(project)
        os.system('git pull')
    if os.path.isfile(os.path.expanduser('~/docker-compose.yml')):
        cd('~')
        os.system('docker-compose up -d --build')


app.mount('/hook', hook)