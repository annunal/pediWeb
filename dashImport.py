import dash as dash
from dash import html,dcc
from flask import Flask, redirect
import flask as flask
import urllib as urllib

#from dash.dependencies import Input, Output, State
from dash import Input, Output, State


import socket,platform,os



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# per pythonanywhere
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#appserver=app.server

#per windows server 2019
server = Flask(__name__)
app = dash.Dash(server=server, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)
app.title = 'pediWeb'
server = app.server

app.config.suppress_callback_exceptions = True
#
#app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
#wsgi_app = app.wsgi_app







