#import dash_bootstrap_components as dbc
from dashImport import app,html,dcc
import base64,os
from CONF import SAVEDIR,cookieGetSet,dbname
from utilities import checkUsPw,tds,fnull
from dbase import dbase

def Navbar(mode='',uidEnc=''):
     try:
        #print(' entro in cookie')
        UPenc=cookieGetSet('dash pedweb cookie')
        #print ('Upenc=',UPenc)
        authState,user,pwd,name,pal,userID,emailID=checkUsPw(UPenc)
        if uidEnc!='':
            userID=uidEnc
        db=dbase(dbname)
        intestazione=db.getTableRecord('users','ID='+format(userID))[0]
#        print('inte',intestazione)
        db.close()
        #print(authState,user,pwd,name)
     except Exception as e:
        print('exception ',e)
        authState=False
        user=''
        Intestazione=[]
     image_filename = SAVEDIR+os.sep+'_images'+os.sep+'pediweb.png' # replace with your own image
     encoded_image = base64.b64encode(open(image_filename, 'rb').read())
     if mode=='' or mode=='print':     
         intLines=[]
         for k in range(8):
            line=intestazione['inte'+format(k)]
            if k==0:
                st={'font-size':'12px','font-weight':'900'}
                print (st)
                first=False
            else:
                st={'font-size':'10px','font-weight':'700'}
            #if line !='' or True:
            intLines.append(html.Div(line,style=st))
         testata=html.Div(intLines)
     elif mode=='HTML':
         testata=''
         for k in range(8):
             line=intestazione['inte'+format(k)]
             if k==0:
                testata +='<B>'+ fnull(line) +'</B><br>'
             else:
                testata += fnull(line) +'<br>'
         return testata
     elif mode=='login':
         testata=html.A([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),style={'height':'100px'}),],href='http://croma.pythonanywhere.com/')

     text_input_style = {'justify-content': 'center', 'align-items': 'center'}
     tdstyle={'width':'270px', 'background-color':'rgb(102,153,255)', 'color':'navy',
              'font-weight':'bold','font-size':'14px','padding':'2px'}
     astyle={ 'background-color': 'navy','font-weight':'bold','font-size':'14px','color':'white','padding': '1px 25px','text-align':'center', 'text-decoration':'none',  'display':'inline-block'}
     adminstyle={ 'background-color': 'red','font-weight':'bold','font-size':'14px','color':'white','padding': '1px 25px','text-align':'center', 'text-decoration':'none',  'display':'inline-block'}
     buttonStyle= {'background-color': 'navy','color':   'white', 'padding': '6px 12px','text-align': 'center',
                   'text-decoration': 'none', 'display': 'inline-block', 'font-size': '15px', 'margin': '4px 2px',
                   'cursor': 'pointer','border':'1px solid transparent', 'border-radius':'230px','padding':'5px'}
     if mode=='' or mode=='login':
         navbar = html.Center([testata, html.Center(html.Table([
             html.Tr([
                 html.Td('', style=tdstyle),
                 html.Td(html.A('Home',href='/',style=buttonStyle), style=tdstyle),
                 html.Td(html.A('Pazienti',href='/listaPazienti', style=buttonStyle), style=tdstyle),
                 html.Td(html.A('Visite',href='/listaVisite', style=buttonStyle), style=tdstyle),
                 #html.Td(html.A('Grafici',href='/plots', style=buttonStyle), style=tdstyle),
                 #html.Td(html.A('Gruppi',href='/gruppi', style=buttonStyle), style=tdstyle),
                 html.Td(html.A('Logout',href='/logout', style=buttonStyle), style=tdstyle),

                 ]
                 )],style={'width':'600px'}))
                ])
     elif mode=='print':
                #intLines.append(html.Br())
         navbar=html.Center(html.Table(html.Tr([html.Td(intLines,style=tds(250)),
                                    html.Td('',      style=tds(480))]
                                   )
                           ))
     else:
         navbar = html.Div(testata)

    # navbar = html.Div([testata])

     return navbar

