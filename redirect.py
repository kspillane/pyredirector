#!/usr/bin/python

import os, configparser
from flask import Flask,redirect,abort,request,send_from_directory,render_template
from datetime import datetime

def load_config():
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

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('templates/css/', path)

@app.route('/vendor/<path:path>')
def send_js(path):
    print('Getting vendor. Path is: ' + path)
    return send_from_directory('templates/vendor/', path)

@app.route('/redir')
def send_index():
    return render_template('child.html')

@app.route('/redir/local')
def view_local_srv():
    return render_template('child.html', ip=ip, title='Local Redirection', localsrv=localsrv)

@app.route('/redir/remote')
def view_remote_srv():
    return render_template('child.html', title='Remote Redirection', **remotesrv)

@app.route('/redir/default')
def view_defaults():
    return render_template('child.html', ip=bind_addr, port=listen_port, title='Default')

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
    load_config()
    app.run(host=bind_addr, port=int(listen_port), debug='True')

