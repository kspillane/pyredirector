####PyRedirector

A URL redirector written in Python using Flask.

Requires: Python 2.7+ with Flask and ConfigParser installed.

##Why?

I run a media server with a bunch of Docker containers to handle automation and services.
Since the containers all run on different ports, it is hard to keep track of all of them.
I decided to write a URL recirector to help simplify access, and so I can better learn Python.

##What is a URL redirector?

Suppose you have two web applications running:

```
Server One - http://foo.com:1500/
Server Two - http://foo.com:8000/
Server Three - http://foo.com:25556/
```
And you have trouble remembering what ports each web app's interface is at, this program allows you to do:

```
http://foo.com/server1 -> http://foo.com:1500/
http://foo.com/server2 -> http://foo.com:8000/
http://foo.com/server3 -> http://foo.com:2556/
```

So as long as your web browser supports HTTP1.1 (which it does), typing in the first address will automatically load the page at the second address.

This is my first time doing a real Python project, first time using flask, and first time putting something on GitHub.

Still a work in progress...

###How to Install and Run:

Install prerequisites (see above - if you don't know how, come back when I have better documentationm or message me)

```
cd ~
git clone https://github.com/kspillane/pyredirector/
cd pyredirector
Setup your redirects in redirect.ini (see that file for instructions)
python redirect.py
```
Open http://your-ip:5000/some_redirect_path_you_specificed_in_the_config

Tested on Ubuntu 16.04