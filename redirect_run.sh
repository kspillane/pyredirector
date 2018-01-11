#!/bin/sh

#
# Launcher script to simplify launching PyRedirector
#

gunicorn -d -c  guni.conf redirect:app
echo "Started PyRedirector and moved to background"

