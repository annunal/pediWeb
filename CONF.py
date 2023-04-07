import os,platform
import flask,dash
import socket,platform,os
import datetime
from dbase import dbase

def cookieGetSet(cookieName,value='', force=False):
        if value !='' or force:
            dash.callback_context.response.set_cookie(cookieName,value)
            return ''
        else:
            allcookies=dict(flask.request.cookies)
            if cookieName in allcookies:
                value= allcookies[cookieName]
            return value

def printLog(*a):
    try:
        baseApp=cookieGetSet('baseApp')
#        if baseApp=='':
#            return
        fnameLog=SAVEDIR+os.sep+'_logs'+os.sep+'logApp.txt'

        #if os.path.exists(fnameLog):
        #    dcrea=creation_date(fnameLog)
        #    age=elapsedHours(dcrea)
            #if elapsedHours(dcrea)>1:
            #    os.remove(SAVEDIR+'_logs/logApp.txt')
        if not os.path.exists(SAVEDIR+os.sep+'_logs'+baseApp):
            os.makedirs(SAVEDIR+os.sep+'_logs/'+baseApp)
        f=open(fnameLog,'a')
        now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(now+': '+  str(a)[1:][:-1] +'\n')
        f.close()
        print(*a)
    except:
        print(*a)

platform=platform.system()
if 'Linux' in platform:
    system='LINUX'
    dire0=os.getcwd()+'/'
else:
    system='WINDOWS'
    dire0=os.getcwd()+'\\'

SAVEDIR=dire0+'_storage'
DATADIR=SAVEDIR+os.sep+'_data'    #  dopo deve essere cosi'

dbname=DATADIR+os.sep+'pediatra.sqlite'


ftphost='80.88.86.108'
ftpuser='ftp9214855'
ftpPass='Ecml2011@'
ftpRemDir='httpdocs/db/MAIL'
