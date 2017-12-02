import os, configparser
from flask import Flask,redirect,abort

config = configparser.ConfigParser()
config.read('redirect.ini')
localsrv = config['LOCAL-SERVERS']
ip = config['DEFAULTS']['localip']
app = Flask(__name__)

@app.route('/<path:path>')
def hello(path):
    for k,v in localsrv.items():
	if path == k:
	    url = 'http://'+ ip + ':' + v
	    return redirect(url, code=302)
    abort(404)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
