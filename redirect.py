import os, configparser
from flask import Flask,redirect,abort,request,send_from_directory,render_template
from datetime import datetime

#Define default config for when no config file exists
def set_default_config():
    #Setup global variables
    global ip
    global bind_addr
    global listen_port
    global logging
    global logfile

    ip = "127.0.0.1"
    bind_addr = "0.0.0.0"
    listen_port = "5000"
    logging = "True"
    logfile = "redirect.log"

    write_config();

    return

#Update the configuration file with the values form the globals
def write_config():
    config = configparser.ConfigParser()

    config['DEFAULTS'] = {}
    config['DEFAULTS']['localip'] = ip
    config['DEFAULTS']['listen_port'] = listen_port
    config['DEFAULTS']['bind_ip'] = bind_addr
    config['LOCAL-SERVERS'] = {}
    config['REMOTE-SERVERS'] = {}
    config['LOGGING'] = {}
    config['LOGGING']['logging'] = logging
    config['LOGGING']['logfile'] = logfile
    
    fh = open('redirect.ini', 'w+')
    config.write(fh)
    fh.close()

    load_config()
    
    return

#Read config file to globals
def load_config():
    config = configparser.ConfigParser()

    #Setup global variables
    global localsrv
    global remotesrv
    global ip
    global bind_addr
    global listen_port
    global logging
    global logfile

    if not os.path.exists('redirect.ini'):
       set_default_config()

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

#Add requests to logfile if enabled
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
#Hanfle requests for css
def send_css(path):
    return send_from_directory('templates/css/', path)

@app.route('/vendor/<path:path>')
#Handle requests for scripts
def send_js(path):
    print('Getting vendor. Path is: ' + path)
    return send_from_directory('templates/vendor/', path)

@app.route('/redir')
def send_index():
    return render_template('child.html')

@app.route('/redir/local_add', methods=['POST'])
#Update Local Server
def update_local():
    global localsrv
    localsrv.update({request.form['path'] : request.form['port']})
    write_config()
    return render_template('child.html', ip=ip, title='Local Redirection', localsrv=localsrv)

@app.route('/redir/remote_add', methods=['POST'])
#Update Remote Server
def update_remote():
    global remotesrv
    remotesrv.update({request.form['path'] : request.form['url']})
    write_config()
    return render_template('child.html', title='Remote Redirection', remotesrv=remotesrv)

@app.route('/redir/local')
#Display Local Servers
def view_local_srv():
    return render_template('child.html', ip=ip, title='Local Redirection', localsrv=localsrv)

@app.route('/redir/remote')
#Display remote servers
def view_remote_srv():
    return render_template('child.html', title='Remote Redirection', remotesrv=remotesrv)

@app.route('/redir/default')
#Display default settings
def view_defaults():
    return render_template('child.html', ip=bind_addr, port=listen_port, title='Default')

@app.route('/<path:path>')
#Main redirect handler
def do_redirects(path):
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

