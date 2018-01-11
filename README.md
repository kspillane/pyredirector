# PyRedirector

## What is PyRedirector and why would I want to use it?

PyRedirector is a simple, easy to use, Flask based web app for setting up URL redirects to local and remote servers.  

It is mainly geared toward homelab people, people who run media stacks, docker or virtual machine administrators, and intranet users. I decided to write it to get better at Python and to make it easier to access my media stack services.  

# Installation

## Requirements  

* Python
* Gunicorn
* Flask
* git  

```
pip install gunicorn
pip install flask
```  
## To install and run
```
cd ~
git clone https://github.com/kspillane/pyredirector
cd pyredirector
gunicorn -c guni.conf redirect:app
```  
> You can also do ```gunicorn -d -c gubi,cinf redirect:app``` to automatically run it in the background.
> Or run the ```redirect_run.sh``` script to save you the trouble of typing it all out.  

Access ```http://server-ip:5000/admin``` to access the web interface to change settings, view logs, and add redirects.  
>You can also run PyRedirector by doing ```python redirect.py``` but this is not advised. See [the Flask page](http://flask.pocoo.org/docs/0.12/deploying/) for more.

# Getting Help

## Issues, Ideas, Requests, and Bugs
Use [the issue tracker](https://github.com/kspillane/pyredirector/issues) to report issues, bugs, ideas, feature requests, and general support questions that you can't find the answer to in the [wiki](https://github.com/kspillane/pyredirector/wiki).

## Usage
See the [wiki](https://github.com/kspillane/pyredirector/wiki) for information how to use the features of the admin site.  

You can also directly edit ```redirect.ini``` to add redirects and make settings changes. It is generated on first run and it pretty self-explanatory.

## Roadmap and TODO

See the [Roadmap](https://github.com/kspillane/pyredirector/wiki/Roadmap) wiki page for more information.






