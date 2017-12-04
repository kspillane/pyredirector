#!/usr/bin/python

import os, configparser
from flask import Flask,redirect,abort,request
from datetime import datetime

def do_config():
    config = configparser.ConfigParser()
    
    global localsrv
    global remotesrv
    global ip
    global bind_addr
    global listen_port
    global logging
    global logfile

    if not os.path.exists('redirect.ini'):
	config['DEFAULTS'] = {}
	config['DEFAULTS']['localip'] = ''
	config['DEFAULTS']['listen_port'] = '5000'
	config['DEFAULTS']['bind_ip'] = '0.0.0.0'
	config['LOCAL-SERVERS'] = {}
	config['REMOTE-SERVERS'] = {}
	config['LOGGING'] = {}
	config['LOGGING']['logging'] = 'false'
	config['LOGGING']['logfile'] = 'pyredirect.log'
	
	fh = open('redirect.ini', 'w+')
	config.write(fh)
	fh.close()

    config.read('redirect.ini')
    localsrv = config['LOCAL-SERVERS']
    remotesrv = config['REMOTE-SERVERS']
    ip = config['DEFAULTS']['localip']
    bind_addr = config['DEFAULTS']['bind_ip']
    listen_port = config['DEFAULTS']['listen_port']
    logging = config['LOGGING']['logging']
    logfile = config['LOGGING']['logfile']

    return

app = Flask(__name__)

def do_logging(url):
    if logging.upper() == 'TRUE':
        timestamp = str(datetime.now())
	path = request.path
        ip = request.remote_addr
        logentry = timestamp + " " + path + " acceessed by " + ip + " redirected to " + url + " \n"

	if os.path.exists(str(logfile)):
	    mode = 'a+'
	else:
	    mode = 'w+'
        fh = open(str(logfile), mode)
	fh.write(logentry)
        fh.close()

    return

@app.route('/<path:path>')
def hello(path):
    for k,v in localsrv.items():
	if path == k:
	    url = 'http://'+ ip + ':' + v
	    do_logging(url)
	    return redirect(url, code=302)
    for k,v in remotesrv.items():
	if path == k:
	    do_logging(v)
	    return redirect(v, code=302)
    do_logging("Error 404 - Not Found")
    abort(404)

if __name__ == '__main__':
    do_config()
    app.run(host=bind_addr, port=int(listen_port), debug='FALSE')
