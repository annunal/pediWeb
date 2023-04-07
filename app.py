# Importazione vecchio database:
# Aprire il vecchio con Access e il nuovo con ODBC
# Copiare Pazienti da uno all altro
# update Pazienti set userID=1
# deleted,  cambiarlo in Deleted e farlo TEXT
# update Pazienti set Deleted='False'
# Salvare i records dal database Access tabella Visite in un file tab delimited
# Cambiare la prima riga usando i fields nel db sqlite
# Aggiungere userID
# importare usando sqllite editor
"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
import os
from urllib.parse import urlparse, parse_qs, urlencode
from pathlib import Path
import flask


from dashImport  import app, html, dcc,Input, Output, State,server
from CONF import DATADIR,printLog,cookieGetSet,SAVEDIR
from datetime import datetime
from utilities import checkUsPw,parseDate,getkey
from schedaPaziente import schedaPaziente,getScheda,showVisita,creaPDF
from loginPage import login
from liste import listaPazienti,listaVisite
from cryptography.fernet import Fernet

app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])

@app.callback(Output('page-content', 'children'),
            Input('url', 'pathname'),Input('url', 'href'))
def display_page(pathname,url):
    #return showdatepicker()
    authState=False

    printLog('PID=',os.getpid(),pathname)
    params=parse_qs(urlparse(url).query)
    UPenc1=''
    try:
        if cookieGetSet('dash pedweb cookie') !='':
            timeOfCookie_s=cookieGetSet('dash pedweb cookie setTime')
            print(timeOfCookie_s)
            timeOfCookie=datetime.strptime(timeOfCookie_s,'%Y-%m-%d %H:%M:%S')
            if (datetime.now()-timeOfCookie).seconds>3600:
                UPenc1= ''
                pathname='/logout'
            else:
                UPenc1=cookieGetSet('dash pedweb cookie')
                authState,user,pwd,nameUser,role,userID,emailID=checkUsPw(UPenc1)
                #printLog(authState,">"+UPenc1+"<")

    except Exception as e:
        print(e)
        authState=False
    if not authState:
        print(pathname,params)
        if '/showVisita' in pathname and 'enc' in params:
            idenc=params['enc'][0]
            f=Fernet(getkey())
            p1=f.decrypt(idenc.encode()).decode()           
            id,uid,idPaz=p1.split('||')
            print('id=',id,'uid=',uid)
            return showVisita(uid,id,idPaz,'utente','print',url,emailID,nameUser)
       #     printLog('index line72:',pathname)
        return login(UPenc1,url)
    if '/login' in pathname:
        #updateStatistics('login')
        return login(UPenc1,url)
    elif '/logout' in pathname:
        print('setto cookie null')
        cookieGetSet('dash pedweb cookie', '',True)
        return dcc.Location(pathname="/", id="landingDiv")
    if '/loggedIn' in pathname:
        return schedaPaziente(userID)
    if '/showSummary' in pathname:
        print(pathname)
        if pathname.split('/showSummary')[1].startswith('/'):
            id=pathname.split('/showSummary')[1][1:]
            print(id)
            if '?' in id:
                id=id.split('?')[0]
            params={'id':[id]}
            print(params)
        if 'id' in params:
            codicePaziente=params['id'][0]
            return schedaPaziente(userID,codicePaziente,False,True)
        else:
            return schedaPaziente(userID)
    elif '/listaPazienti' in pathname:
        return listaPazienti()
    elif '/listaVisite' in pathname:
        return listaVisite()

    elif '/showVisita' in pathname:
        if 'id' in params:
            pr='';us=''
            codVisita=params['id'][0]
            if 'idPaz' in params:
                idPaz=params['idPaz'][0]
            else:
                idPaz=''
        elif 'enc' in params:
                pr='print'
                us='user'
                idenc=params['enc'][0]
                f=Fernet(getkey())
                enc=f.decrypt(idenc.encode()).decode()           
                codVisita,userID,idPaz=enc.split('||')

        print('codVisita=',codVisita,pr)
        return showVisita(userID,codVisita,idPaz,us,pr,url,emailID,nameUser)
    else:
        return schedaPaziente(userID)

#@app.route('/')

#@app.server.route("/get_visita")
@app.server.route('/get_visita', defaults={'path': ''})
@app.server.route('/<path:path>')
#def url_redirector(path):


def get_report(path):
    print(path)
    HERE = Path(__file__).parent
    UPenc1=cookieGetSet('dash pedweb cookie')
    authState,user,pwd,nameUser,role,userID,emailID=checkUsPw(UPenc1)
    if authState:
        codeVisita =flask.request.args.get('codeVisita')
        print(SAVEDIR+os.sep+'_temp'+os.sep+"visita_"+format(codeVisita)+".pdf")
        #if not os.path.exists(SAVEDIR+os.sep+'_temp'+os.sep+"visita_"+format(codeVisita)+".pdf") : 
        outFilePDF=creaPDF(userID,codeVisita)
        if os.path.exists(SAVEDIR+os.sep+'_temp'+os.sep+"visita_"+format(codeVisita)+".pdf") :    
            return flask.send_from_directory(SAVEDIR+os.sep+'_temp',"visita_"+format(codeVisita)+".pdf")
        else:
            return ''
    else:
        return ''


#import json
from dbase import dbase
from CONF import dbname
if __name__ == '__main__':
    print('PID=',os.getpid())
# UPDATE DATAVISITE
    UpdateDB=False
    if UpdateDB:
        db=dbase(dbname)
        recs=db.getTableRecord('Visite')
        n=0
        for rec in recs:
            id=rec['CodiceVisita']
            data=rec['DataVisita']
            n+=1
            if data==None: continue
            if '/' in data:
                dv=parseDate(data)
                newData=dv.strftime('%Y-%m-%d 00:00')
                print(n,len(recs))
                sql='update Visite set [DataVisita]=\''+newData+'\' WHERE CodiceVisita='+format(id)
                db.execSQL(sql)
        db.close()
    #sql='update Pazienti set [Deleted]=\'False\''
    #db.execSQL(sql)
    #db.close()
    #showVisita(16269)    
    appserver=app.server
  
    #app.run_server(debug=True)
    app.server.run()


