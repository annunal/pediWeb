from encodings import normalize_encoding
from dashImport import html,dcc,app,Input,Output,State
from datetime import datetime,timedelta
from CONF import DATADIR,dbname
from dbase import dbase
from utilities import *
from dash import ctx
from Navbar import Navbar
from plots import plots
from utilities import *
import numpy as np

tdslab=tds('','','','navy','','white','right')
tdsval=tds('','','','','bold','navy')

def getNomi(letters='', namePattern='', locationPattern='', anno=''):
    print(letters,namePattern,locationPattern,anno)
    blet=letters=='' or letters ==None or letters ==[]
    if blet and (namePattern=='' or namePattern==None) and (locationPattern=='' or locationPattern==None) and (anno=='' or anno==None):
        return ''
    where1=''
    whereNome='';whereAnno='' ;whereLocation=''
    if not blet:
       for lett in letters:
            if where1 !='':
                where1 +=' OR '
            where1 +=' Cognome like \''+lett+'%\''
    if where1 !='':
        where1='('+where1+')'
    if namePattern !='':
        whereNome='([Cognome] like \''+namePattern+'%\')'
    if locationPattern !='':
        whereLocation='([LuogodiNascita] like \''+locationPattern+'%\')'
    if anno !='':
        whereAnno='(DatadiNascita LIKE \'%'+format(anno)+'%\')'
    db=dbase(dbname)
    sql='SELECT Cognome,Nome,Codicepaziente,LuogodiNascita,DatadiNascita from Pazienti where  ([Deleted]=\'False\' or [Deleted] is Null)'
    if where1 !='':
        sql +=' AND '+where1
    if whereNome!='':
        sql +=' AND '+whereNome
    if whereLocation!='':
        sql +=' AND '+whereLocation
    if whereAnno!='':
        sql +=' AND '+whereAnno
    sql +=' ORDER BY LOWER(Cognome),LOWER(Nome)'
    print(sql)
    recs=db.getRecord(sql)
    db.close()
     
    rows=[]
    tabdiv=''
    if recs !=[]:
        for rec in recs:
            #print(rec)
        
            Cognome,Nome,Codicepaziente,LuogodiNascita,DatadiNascita=rec
            year=parseDate(DatadiNascita).strftime('%Y')
            row=html.Tr([html.Td(html.A(fnull(Cognome)+' '+fnull(Nome), href='/showSummary/'+format(Codicepaziente)
                                        ),style=tds(150,'',12,'','bold')
                                 ),
                         html.Td(fnull(LuogodiNascita)+' - '+year,style=tds(200,'',10)) ])
            rows.append(row)
                               
        lista=html.Table(rows,style={'maxheight':'500px','overflow':'scroll'})
        tabdiv=html.Div(lista,style={'height':'520px',"overflow": "scroll"})
    return tabdiv


def listaPazienti():    
    classi='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    opt=[]
    for k in range(len(classi)):
        opt.append(classi[k])
    y0=datetime.utcnow().year
    optYY=np.linspace(1950,y0,y0-1950+1)
    commands=html.Table([html.Tr([html.Td('Nome'),html.Td('Luogo di Nascita'),html.Td('Anno di nascita'),html.Td('')]),
                        html.Tr([html.Td(dcc.Input(id='searchName')),
                                 html.Td(dcc.Input(id='searchLocation')),
                                 html.Td(dcc.Dropdown(id='searchAnno',options=optYY,value='')),
                                 html.Td(html.Button('Cerca',id='btnSearch'))
                                 ])
                        ])
    tab=html.Table([html.Tr(html.Td(commands,colSpan=2)),                           
                    html.Tr([html.Td(dcc.Checklist(id='startLetter',options=opt),style=tds(80,'',10)), #{'width':'80px','vertical-align':'top'}),
                             html.Td(id='listaNomi',colSpan=4,style={'width':'400px','vertical-align':'top'})
                             ])
                    ])
    layout=html.Center([Navbar(),'Indica parte del Nome, Luogo o anno di nascita, lettera inizale del cognome e pmemi "Cerca"',tab])
    return layout

def listaVisite():
    defperiodi=[{'label':'Ultimo giorno','value':-1},
                 {'label':'Ultima settimana','value':-7},
                 {'label':'Ultimo mese','value':-30},
                 {'label':'Ultimo anno','value':-365},
            ]
    dateBlockMin=dcc.DatePickerSingle(
        id='datemin',min_date_allowed=datetime(1950, 1, 1),
        max_date_allowed=datetime(2050, 9, 19),
        placeholder='D MMM YYYY',
        display_format='D MMM YYYY',
        initial_visible_month=datetime.utcnow(),
                     )
    dateBlockMax=dcc.DatePickerSingle(
        id='datemax',min_date_allowed=datetime(1950, 1, 1),
        max_date_allowed=datetime(2050, 9, 19),
        placeholder='D MMM YYYY',
        display_format='D MMM YYYY',
        initial_visible_month=datetime.utcnow(),
                     )
    
    commands=html.Table([ html.Tr([html.Td('Periodo',style=tds(200)),
                                   html.Td('Data iniziale',style=tds(100)),
                                   html.Td('Data finale',style=tds(100)),
                                   html.Td('Cerca parole',style=tds(200))]),
                            html.Tr([html.Td(dcc.Dropdown(id='periodo',options=defperiodi),style={'width':'200px'}),
                                 html.Td(dateBlockMin,style={'width':'100px'}),
                                 html.Td(dateBlockMax,style={'width':'100px'}),
                                 html.Td(dcc.Input(id='searchWord'),style={'width':'200px'}),
                                 html.Td(html.Button('Cerca',id='btnSearchVisite'),style={'width':'200px'})
                                 ])
                        ])
    lista=html.Div(id='listaVisite')
    tab=html.Center([Navbar(),commands,html.Br(),lista])
    return tab

def getListaVisite(periodo,dateMin,dateMax,searchWord):
    if fnull(periodo) !='':
        dateMax=datetime.utcnow()
        dateMin=dateMax+timedelta(days=periodo)
        dateMin=dateMin.strftime('%Y-%m-%d')
        dateMax=dateMax.strftime('%Y-%m-%d')
    whereDate='';whereWord=''
    if fnull(dateMin) !='':
        whereDate='[DataVisita]>=\''+dateMin+'\''
    if fnull(dateMax) !='':
        if whereDate !='':
            whereDate +=' AND '
        whereDate+='[DataVisita]<=\''+dateMax+'\''
    if fnull(searchWord) !='':
        searchWord=searchWord.lower()
        whereWord='(LOWER([MotivodellaVisita]) LIKE \'%'+searchWord+'%\') OR'
        whereWord+='(LOWER([Problemisegnalatidaigenitori]) LIKE \'%'+searchWord+'%\') OR '
        whereWord+='(LOWER([EventualiRilievi]) LIKE \'%'+searchWord+'%\') OR '
        whereWord+='(LOWER([Sintesidellosservazione]) LIKE \'%'+searchWord+'%\') OR '
        whereWord+='(LOWER([Suggerimenti]) LIKE \'%'+searchWord+'%\')'
    if whereWord+whereDate=='':
        return '',dateMin,dateMax

    sql='SELECT visite.CodiceVisita,visite.DataVisita, visite.[Eta(anni/mesi/giorni)], visite.Paziente, pazienti.Cognome, pazienti.Nome, pazienti.DatadiNascita, pazienti.LuogodiNascita, pazienti.Comune FROM pazienti INNER JOIN visite ON pazienti.Codicepaziente = visite.Paziente'
    sql+=' WHERE (LOWER([Visite].[deleted])=\'false\' or [Visite].[deleted] is Null) '
    if whereDate !='':
        sql +=' AND ('+whereDate+')'
    if whereWord !='':
        sql +=' AND ('+whereWord+')'
    sql +=' ORDER BY [DataVisita] desc'
    print(sql)
    db=dbase(dbname)
    recs=db.getRecord(sql)
    db.close()
     
    rows=[]
    tabdiv=''
    if recs !=[]:
        for rec in recs:
            #print(rec)
        
            CodiceVisita,DataVisita, Eta,CodicePaz, Cognome, Nome, DatadiNascita, LuogodiNascita, Comune=rec
            print(DataVisita,DatadiNascita)
            dvS=parseDate(DataVisita).strftime('%d/%m/%Y')
            year=parseDate(DatadiNascita).strftime('%Y')
            testo=fnull(Cognome)+' '+fnull(Nome)+' (n.:'+fnull(LuogodiNascita)+', '+year+' - '+fnull(Eta)+' c:'+fnull(Comune)+')'
            row=html.Tr([html.Td(html.A(dvS, href='/showVisita?id='+format(CodiceVisita)
                                        ),style=tds(80,'',12,'','bold')
                                 ),
                         html.Td(testo,style=tds(400,'',10)) ])
            rows.append(row)
                               
        lista=html.Table(rows,style={'maxheight':'500px','overflow':'scroll'})
        tabdiv=html.Div(lista,style={'height':'520px',"overflow": "scroll"})
    return tabdiv,dateMin,dateMax

@app.callback(Output('listaNomi','children'),
              Input('btnSearch','n_clicks'),
              State('startLetter','value'),
              State('searchName','value'),
              State('searchLocation','value'),
              State('searchAnno','value'))
def selez(nclick,letters,searchName,searchLocation,searchAnno):
    print (letters,searchName,searchLocation,searchAnno)

    return getNomi(letters,fnull(searchName),fnull(searchLocation),fnull(searchAnno))

@app.callback(Output('listaVisite','children'),
              Output('datemin','date'),
              Output('datemax','date'),
              Input('btnSearchVisite','n_clicks'),
              State('periodo','value'),
              State('datemin','date'),
              State('datemax','date'),
              State('searchWord','value'))
def selez(nclick,periodo,dateMin,dateMax,searchWord):
    print (periodo,dateMin,dateMax,searchWord)
    lista,dateMin,dateMax=getListaVisite(periodo,dateMin,dateMax,searchWord)
    return lista,dateMin,dateMax