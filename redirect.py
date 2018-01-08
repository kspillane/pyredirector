import os, configparser, re, sys, time, signal
from flask import Flask,redirect,abort,request,send_from_directory,render_template,url_for
from datetime import datetime
from multiprocessing import Process, Queue

global admin_url

admin_url = "admin"

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

def load_bind():
    load_config()

    return str(bind_addr + ":" + listen_port)

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

#Define default config for when no config file exists
def set_default_config():
    global ip
    global bind_addr
    global listen_port
    global logging
    global logfile

    ip = "127.0.0.1"
    bind_addr = "0.0.0.0"
    listen_port = "5000"
    logging = "true"
    logfile = "redirect.log"

    write_config()

    return

#Update the configuration file with the values form the globals
def write_config():
    config = configparser.ConfigParser()

    config['DEFAULTS'] = {}
    config['DEFAULTS']['localip'] = ip
    config['DEFAULTS']['listen_port'] = listen_port
    config['DEFAULTS']['bind_ip'] = bind_addr
    config['DEFAULTS']['admin_url'] = admin_url
    config['LOCAL-SERVERS'] = {}
    config['REMOTE-SERVERS'] = {}
    config['LOGGING'] = {}
    config['LOGGING']['logging'] = logging
    config['LOGGING']['logfile'] = logfile

    for i, v in remotesrv.items():
        config['REMOTE-SERVERS'][i] = v
    for i, v in localsrv.items():
        config['LOCAL-SERVERS'][i] = v

    fh = open('redirect.ini', 'w+')
    config.write(fh)
    fh.close()

    load_config()

    return

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

#Regex to make sure the form data submissions is valid
def validate_form(valdata):
    for data, pattern in valdata.items():
        val = re.match(pattern, data)
        if not val:
            return data
    return

def update_logs():
    global logfile
    global logging

    if str(request.form.get('logging')) == "true":
            logging = "true"
    else:
            logging = "false"

    if not os.path.exists(str(request.form['logfile'])):
        with open(str(request.form['logfile']), 'a'):
            os.utime(str(request.form['logfile']), "None")

    logfile = str(request.form['logfile'])

    return


def restart():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    some_queue.put("TRUE")
    

app = Flask(__name__)

@app.route('/css/<path:path>')
#Hanfle requests for css
def send_css(path):
    return send_from_directory('templates/css/', path)

@app.route('/vendor/<path:path>')
#Handle requests for scripts
def send_js(path):
   return send_from_directory('templates/vendor/', path)

@app.route(str('/' + admin_url))
#Default admin landing page
def send_index():
    do_logging("ADMIN - admin landing page")

    return render_template('child.html')

@app.route(str("/" + admin_url + "/default_update"), methods=['POST'])
def update_defaults():
    global bind_addr
    global listen_port
    global admin_url
    global to_reload
    global ip
        
    ip_pattern = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    port_pattern = "^\d{4,5}$"
    formdata = {request.form['ip']: ip_pattern, request.form['port']: port_pattern}
    valdata = validate_form(formdata)

    if valdata:
        print "there was a problem with entry: " + valdata
        abort(403)
        return

    bind_addr = str(request.form['ip'])
    listen_port = str(request.form['port'])
    admin_url = str(request.form['admin_url'])
    ip = str(request.form['local_ip'])

    update_logs()
    write_config()
    do_logging("ADMIN - update defaults - Reloading...")
    restart()

    return redirect(str("http://" + ip + ":" + listen_port + "/" + admin_url + "/default"), code="302")

@app.route(str("/" + admin_url + "/local_add"), methods=['POST'])
#Update Local Server
def update_local():
    port_pattern = "^\d{4,5}$"
    formdata = {request.form['port']: port_pattern}
    valdata = validate_form(formdata)

    if valdata:
        print "there was a problem with entry: " + valdata
        abort(403)
        return

    localsrv.update({str(request.form['path']) : str(request.form['port'])})
    write_config()
    do_logging("ADMIN - add local redirect")

    return redirect(url_for('view_local_srv'))

@app.route(str("/" + admin_url + "/local_delete"), methods=['POST'])
#Delete local redirects
def delete_local():
    global localsrv

    del localsrv[str(request.form['redir_del'])]
    write_config()
    do_logging("ADMIN - delete local redirect")

    return redirect(url_for('view_local_srv'))

@app.route(str("/" + admin_url + "/remote_add"), methods=['POST'])
#Update Remote Server
def update_remote():
    remotesrv.update({str(request.form['path']) : str(request.form['url'])})
    write_config()
    do_logging("ADMIN - add remote redirect")

    return redirect(url_for('view_remote_srv'))

@app.route(str("/" + admin_url + "/remote_delete"), methods=['POST'])
#Delete remote redirects
def delete_remote():
    global remotesrv

    del remotesrv[str(request.form['redir_del'])]
    write_config()
    do_logging("ADMIN - delete remote redirect")

    return redirect(url_for('view_remote_srv'))

@app.route(str("/" + admin_url + "/local"))
#Display Local Servers
def view_local_srv():
    do_logging("ADMIN - view Local redirects")

    return render_template('child.html', ip=ip, title='Local Redirection', localsrv=localsrv)

@app.route(str("/" + admin_url + "/remote"))
#Display remote servers
def view_remote_srv():
    do_logging("ADMIN - view remote redirects")

    return render_template('child.html', title='Remote Redirection', remotesrv=remotesrv)

@app.route(str("/" + admin_url + "/default"))
#Display default settings
def view_defaults():
    do_logging("ADMIN - view default settings")

    return render_template('child.html', ip=bind_addr, port=listen_port, logfile=logfile, logging=logging, admin_url=admin_url, local_ip=ip, title='Default')

@app.route(str("/" + admin_url + "/logs"))
#Display remote servers
def view_logs():
    do_logging("ADMIN - view logs")

    if logging:
        fh = open(str(logfile), "r")
        logs = fh.readlines()
        fh.close
        return render_template('child.html', title='Redirect Access Logs', log=reversed(logs))
    else:
        return render_template('child.html', title='Redirect Access Logs')

@app.route(str("/" + admin_url + "/clear_logs"), methods=['POST'])
def clear_logs():
    if str(request.form['clearlogs']) == '1':
        print "we made it here"
        open(logfile, 'w').close()

    do_logging("ADMIN - Clear Logs")

    return redirect(url_for('view_logs'))

@app.route('/<path:path>')
#Main redirect handler
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

def start_flaskapp():
        load_config()
        app.run(host=bind_addr, port=int(listen_port), debug=True)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    start_flaskapp()
