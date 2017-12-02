#!/usr/bin/python

import os, configparser
from flask import Flask,redirect,abort

config = configparser.ConfigParser()
config.read('redirect.ini')
localsrv = config['LOCAL-SERVERS']
ip = config['DEFAULTS']['localip']
bind_addr = config['DEFAULTS']['bind_ip']
listen_port = config['DEFAULTS']['listen_port']

app = Flask(__name__)

@app.route('/<path:path>')
def hello(path):
    for k,v in localsrv.items():
	if path == k:
	    url = 'http://'+ ip + ':' + v
	    return redirect(url, code=302)
    abort(404)

if __name__ == '__main__':
    app.run(host=bind_addr, port=int(listen_port), debug='FALSE')
