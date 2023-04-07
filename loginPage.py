
from dashImport import app,html,dcc
from dash import ctx
from dash.dependencies import Input, Output, State
from CONF import cookieGetSet,printLog
from cryptography.fernet import Fernet
import json
from datetime import datetime
from utilities import checkUsPw,EncUsPw,sendMail,sendMail,DecUsPw,tds
from Navbar import Navbar

import urllib
from urllib.parse import urlparse, parse_qs, urlencode

tdst=tds()
tdReg=''
td30=tdst.copy();td70=tdst.copy()
td30['width']='200px'
td70['width']='400px'
stBut=tdst.copy()
stBut['backgroundColor']='LightBlue' 
tdInp=tdst.copy()
tdInp['width']='100%'
tdInp['font-size']='30px'


def login(UPenc,url):
    parse_result = urlparse(url)
    baseurl=parse_result.scheme+'://'+parse_result.netloc
    
    authState,user,pwd,nameUser,role,userID,emailID=checkUsPw(UPenc)
    loginBlock=html.Div([html.Div('Indicare utente e password',id='labelLogin'), html.Br(),
                 html.Table([html.Tr(html.Td(tdReg, colSpan=2)),


                     html.Tr([
                    html.Td('Utente',style=td30),
                    html.Td(dcc.Input(id='login_username',type='text',value=user,style=tdst),style=td70),
                    ]),
                  html.Tr([
                    html.Td('Password',style=td30),
                    html.Td(dcc.Input(id='login_pwd',type='password',value=pwd,style=tdInp),style=td70),
                    ]),


                  html.Tr([
                    html.Td(' ',style=td30),
                    html.Td(html.Button('Entra',id='Enterlogin',n_clicks=0,style=stBut),style=td70)
                    ]),


                  ])
                ],style={'width':'500px'})

    myurl={'returnurl=':'/loggedIn','service': baseurl}
    myurlenc=urllib.parse.urlencode(myurl)

    boldStyle={'font-size':'14px','font-weigth':'bold', 'color':'navy'}

    layout   = html.Div([html.Div(id="hidden_div_for_redirect_callback_login"),
                       html.Center([Navbar('login'),loginBlock])])

    return layout



@app.callback(Output('hidden_div_for_redirect_callback_login','children'),
              Output('labelLogin','children'),Output('labelLogin','style'),
              Input('Enterlogin','n_clicks'), State('login_username','value'),
              State('login_pwd','value')
              )
def check_login(nclick,uname,pwd0):
    #printLog('nclick',nclick, uname,pwd0)

    redstyle={"font-weight": "bold",'color':'red'}
    blackstyle={'font-weight':'', 'color':'black'}

    if nclick>0:
        #import flask
        #printLog(uname,pwd0)
       # print(uname,pwd)
        if uname=='' or pwd0==''or uname==None or pwd0==None:
            #SaveEntry(uname,pwd0,'Utente o password nulle')
            return '','Utente o password nulle, per favore introduci un utente e password validi',redstyle
        else:
            #  send message e-ncrypted
            UPenc=EncUsPw(uname,pwd0)
            authState,user,pwd,name,gruppiUser,userID,emailID=checkUsPw(UPenc)
            #printLog(authState,user,pwd,name,gruppiUser,uname,pwd0)
            if authState==True:
                cookieGetSet('dash pedweb cookie', UPenc)
                now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cookieGetSet('dash pedweb cookie setTime', now)
                #printLog(uname,pwd0,'logged In')
                #SaveEntry(uname,pwd0,'logged In')
                if uname !='alessandro':
                    sendMail('alessandro.annunziato@gmail.com','[PEDWEB] logged in '+uname,' utente '+uname+ ' si e loggato')
                #display_page('/')
                #return dcc.Location(pathname="/", id="landingDiv")
                #saveBackup(utentiFilejson,'','%Y%m%d')
                return dcc.Location(pathname="/loggedIn", id="landingDiv"),'',blackstyle
            else:
                #SaveEntry(uname,pwd0,'Utente o password non riconosciute')
                return '', 'Utente o password non riconosciute, per favore riprovare',redstyle
    else:

        return '',html.Div(['Fornisci utente e password'],style=tdst),blackstyle

