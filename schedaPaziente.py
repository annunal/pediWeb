from ctypes import alignment
from encodings import normalize_encoding
from dashImport import html,dcc,app,Input,Output,State
from datetime import datetime
from CONF import DATADIR,dbname,SAVEDIR,ftphost,ftpuser,ftpPass,ftpRemDir,printLog
from dbase import dbase
from utilities import *
from dash import ctx
from Navbar import Navbar
from plots import plots
import base64
import pdfkit
#import dash_bootstrap_components as dbc

tdslab=     tds('','','','navy','','white','right')
tdslabprint=tds('','',12,'rgb(240,240,240)','','black','right','black')

tdsval=tds('','','','','bold','navy')
tdsvalprint=tds('','',14,'','bold','black','black')
pl=plots()

image_filename = SAVEDIR+os.sep+'_images'+os.sep+'email.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
srcEmailImg='data:image/png;base64,{}'.format(encoded_image.decode())

image_filename = SAVEDIR+os.sep+'_images'+os.sep+'printer.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
srcPrintImg='data:image/png;base64,{}'.format(encoded_image.decode())


image_filename = SAVEDIR+os.sep+'_images'+os.sep+'pdfImage.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
srcPDFImg='data:image/png;base64,{}'.format(encoded_image.decode())

def creatab(fields,cols=1,totw=800,mode=''):
    if mode=='HTML':
        sectionHTML=''
    rows=[]
    rowsHTML=[]
    n=0
    row=[]
    rowHTML=[]
    if mode=='':
        tdslab1=tdslab.copy()
        tdsval1=tdsval.copy()
    else:
        tdslab1=tdslabprint.copy()
        tdsval1=tdsvalprint.copy()
        #print('tdslab1=',tdslab1)
    tdslab1['width']=format(totw/cols*0.8)+'px'
    
    tdsval1['width']=format(totw/cols*1.2)+'px'
    tdsval1['border']='solid 1px navy'
    for lab in fields.keys():
        if lab.startswith('TX'):
            lab1=lab.split('TX:')[1]
            if '|' in lab1:
                idField=lab1.split('|')[0]
                lab1=lab1.split('|')[1]
            else:
                idField=''
            
            tdslab1['text-align']='left'
            tdsval1['width']=format(totw)+'px'
            tdslab1['width']=format(totw)+'px'
            if idField=='':
                tbb=html.Table([html.Tr(html.Td(lab1,style=tdslab1)),
                                html.Tr(html.Td(html.Div(fields[lab],style={'height':'70px'}),style=tdsval1))
                ])
            #    tbbHTML='<TABLE><TR><TD colspan=2 class="label">'+lab1+'</TD></TR><TR><TD colspan=2 class="value">'+fields[lab]+'</TD></TR></TABLE>'
            else:
                tbb=html.Table([html.Tr(html.Td(lab1,style=tdslab1)),
                                html.Tr(html.Td(html.Div(fields[lab],id=idField,style={'height':'70px'}),style=tdsval1))
                ])
            tbbHTML='<TABLE><TR><TD colspan=2 class="label2" >'+fnull(lab1)+'</TD></TR><TR><TD colspan=2 class="value2">'+fnull(fields[lab])+'</TD></TR></TABLE>'
            row.append(html.Td(tbb,colSpan=2))
            rowHTML.append('<TD colspan=2>'+tbbHTML+'</TD>')
        elif lab.startswith('ETX:'):            
            lab1=lab.split('|')[1]
            idField=lab.split('|')[0].split('ETX:')[1]
            if lab1=='=':lab1=idField
            tdslab1['text-align']='left'
            tdsval1['width']=format(totw)+'px'
            tdslab1['width']=format(totw)+'px'
            tbb=html.Table([html.Tr(html.Td(lab1,style=tdslab1)),
                            html.Tr(html.Td(dcc.Textarea(value=fields[lab],id=idField,style={'height':'100px','width':'100%'}),style=tdsval1))
            ])
            row.append(html.Td(tbb,colSpan=2))
        elif lab.startswith('RAD:'):
            #disab=False
            #if lab.startswith('RAD:'):disab=True
            lab1=lab.split('|')[1]
            idField=lab.split('|')[0].split('RAD:')[1]
            if lab1=='=':lab1=idField
            options=lab.split('|')[2].split(',')            
            row.append(html.Td(lab1,style=tdslab1))
            row.append(html.Td(dcc.RadioItems(options=options,value=fields[lab],id=idField),style=tdsval1))
            
        elif lab.startswith('ECK'):
            lab1=lab.split('|')[1]
            idField=lab.split('|')[0].split('ECK:')[1]
            if lab1=='=':lab1=idField
            row.append(html.Td(lab1,style=tdslab1))
            
            row.append(html.Td(dcc.Checklist(id=idField,options=[{'label':'','value':'TRUE'}],value=fields[lab]),
                               style=tdsval1))

        elif lab.startswith('CK'):
            lab1=lab[3:]
            row.append(html.Td(lab1,style=tdslab1))
            
            row.append(html.Td(dcc.Checklist([{'label':'','value':'TRUE'}],[fields[lab]]),
                               style=tdsval1))
        elif lab.startswith('DRP'):
            lab1=lab.split('|')[1]
            idField=lab.split('|')[0].split('DRP:')[1]
            if lab1=='=':lab1=idField
            optionsStr=lab.split('|')[2]
            #print(optionsStr)
            options=json.loads(optionsStr)
            row.append(html.Td(lab1,style=tdslab1))
            
            row.append(html.Td(dcc.Dropdown(id=idField,options=options,value=fields[lab],style={'font-size':'12px'}),
                               style={}))

        elif lab.startswith('CH:'):
            #print(lab)
            lab1=lab.split('|')[1]
            if lab1=='=':lab1=idField
            idField=lab.split('|')[0].split('CH:')[1]
            row.append(html.Td(lab1,style=tdslab1))
            row.append(html.Td(html.Div(fields[lab],id=idField),style=tdsval1))
            rowHTML.append('<TD  class="label">'+lab1+'</TD>')
            rowHTML.append('<TD class="value">'+format(fields[lab])+'</TD>')

        elif lab.startswith('INP:'):  # DAT TXE
            #print(lab)
            lab1=lab.split('|')[1]
            idField=lab.split('|')[0].split('INP:')[1]
            if lab1=='=':lab1=idField
            row.append(html.Td(lab1,style=tdslab1))
            row.append(html.Td(dcc.Input(value=fields[lab],id=idField,style={'width':'100%'}),style=tdsval1))
        elif lab.startswith('DAT:'):
            lab1=lab.split('|')[1]
            idField=lab.split('|')[0].split('DAT:')[1]
            if lab1=='=':lab1=idField
            row.append(html.Td(lab1,style=tdslab1))
            dd=datetime.strptime(fields[lab],'%d/%m/%Y')
            dateBlock=dcc.DatePickerSingle(
                id=idField,min_date_allowed=datetime(1950, 1, 1),
                max_date_allowed=datetime(2050, 9, 19),
                placeholder='D MMM YYYY',
                display_format='D MMM YYYY',
                initial_visible_month=datetime.utcnow(),
                date=dd                   )
            row.append(html.Td(dateBlock))

        else:
            if '|' in lab:
                idField=lab.split('|')[0]
                lab1=lab.split('|')[1]
                if lab1=='=':lab1=idField
            else:
                idField=''
                lab1=lab
            row.append(html.Td(lab1,style=tdslab1))
            rowHTML.append('<TD  class="label">'+lab1+'</TD>')
            rowHTML.append('<TD class="value">'+fnull(fields[lab])+'</TD>')
            if idField=='':
                row.append(html.Td(fields[lab],style=tdsval1))                
            else:
                row.append(html.Td(fields[lab],id=idField,style=tdsval1))
        n+=1
        if n==cols:
            rows.append(html.Tr(row))
            rowsHTML.append('<TR>'+''.join(rowHTML)+'</TR>')
            n=0
            row=[]
            rowHTML=[]
    if row !=[]:
        rows.append(html.Tr(row))
        rowsHTML.append('<TR>'+''.join(rowHTML)+'</TR>')
    tab=html.Table(rows)
    tabHTML='<TABLE>'+'\n'.join(rowsHTML)+'</TABLE>'
    if mode=='HTML':
        return tabHTML
    else:
        return tab

def creaTabVisita(userID,codVisita,Edit=False,codPaz='',mode=''):
    db=dbase(dbname)
    
    fields={'Visite.CodiceVisita':0,'Paziente':1,'Cognome':2,'Nome':3,'Sesso':4,
            '[PesoRilevato(gr)]':5,'DataVisita':6,'Peso_percentile':7,
            'Lunghezza_percentile':8,"circonferenza_percentile":9,"CirconferenzaCranica":10,"MotivodellaVisita":11,
            "[Eta(anni/mesi/giorni)]":12,
            "LatteMaterno":13,"AltroLatte":14,"TipodiLatte":15,"IntegrazioneconVitaminaD":16,
            "Problemisegnalatidaigenitori":17,"EventualiRilievi":18,"Sintesidellosservazione":19,"Suggerimenti":20,
            "[Pazienti].Cognome":21, "[Pazienti].Nome":22, "[Pazienti].[DatadiNascita]":23,
           "[Pazienti].Sesso":24, "[Tipivisite].[Tipodivisita] as tp":25,'[Lunghezza(cm)]':26,"[Pazienti].[LuogodiNascita]":27,
           "[Visite].Tipodivisita":28,"[Pazienti].Email":29
            }
    if codPaz=='':
        sql='SELECT '+ ','.join(fields)+' FROM (Visite INNER JOIN [Pazienti] ON Visite.Paziente = [Pazienti].[CodicePaziente]) LEFT JOIN [Tipivisite] ON Visite.[Tipodivisita] = [Tipivisite].[CodiceVisita] WHERE Visite.[CodiceVisita]='+format(codVisita) +' and Pazienti.userID='+format(userID)
        #print(sql)
        rec=db.getRecord(sql)
        if len(rec)>0:
            rec=rec[0]
        else:
            return '',-1,''
    else:
        rs=db.getTableRecord('Pazienti','Codicepaziente='+format(codPaz))[0]
        #print(rs)
        #print('----------------------')
        rec={}
        for f in fields.keys():
            #print(f)
            rec[fields[f]]=''
        rec[fields['Paziente']]=codPaz
        rec[fields['Cognome']]=rs['Cognome']        
        rec[fields['[Pazienti].Email']]=fnull(rs['email'])
        rec[fields['[Pazienti].[LuogodiNascita]']]=rs['LuogodiNascita']
        rec[fields['[Pazienti].[DatadiNascita]']]=rs['DatadiNascita']
        rec[fields['Nome']]=rs['Nome']
        rec[fields['Sesso']]=rs['Sesso']
        rec[fields['DataVisita']]=datetime.utcnow().strftime('%d/%m/%Y 00:00')
    #print('*******',len(rec),rec)
    #for f in fields:
    #    print(f+'=rec[fields[\''+f+'\']]')
    nomeCognome=rec[fields['Nome']]+' '+rec[fields['Cognome']]
    dv=parseDate(rec[fields['DataVisita']])    
    dataVisita=dv.strftime('%d/%m/%Y')
    eta=rec[fields['[Eta(anni/mesi/giorni)]']]    
    CodiceVisita1=rec[fields['Visite.CodiceVisita']]
    Paziente=rec[fields['Paziente']]
    email=fnull(rec[fields['[Pazienti].Email']])
    Cognome=rec[fields['Cognome']]
    Nome=rec[fields['Nome']]
    Sesso=rec[fields['Sesso']]
    PesoRilevato_gr=rec[fields['[PesoRilevato(gr)]']]
    Peso_percentile=rec[fields['Peso_percentile']]
    peso_P=format(PesoRilevato_gr)+'   ('+format(Peso_percentile)+ '%)'

    Lunghezza=rec[fields['[Lunghezza(cm)]']]
    Lunghezza_percentile=rec[fields['Lunghezza_percentile']]
    lung_P=format(Lunghezza)+'   ('+format(Lunghezza_percentile)+ '%)'
    
    circonferenza_percentile=rec[fields['circonferenza_percentile']]
    CirconferenzaCranica=rec[fields['CirconferenzaCranica']]
    circ_P=format(CirconferenzaCranica)+'   ('+format(circonferenza_percentile)+ '%)'

    MotivodellaVisita=rec[fields['MotivodellaVisita']]    
    LatteMaterno=rec[fields['LatteMaterno']]  
    if LatteMaterno=='FALSE':LatteMaterno='No'
    else:LatteMaterno='Si'
    #print('LatteMaterno',LatteMaterno)
    AltroLatte=rec[fields['AltroLatte']]
    if AltroLatte=='FALSE':AltroLatte='No'
    else: AltroLatte='Si'
    TipodiLatte=rec[fields['TipodiLatte']]
    IntegrazioneconVitaminaD=rec[fields['IntegrazioneconVitaminaD']]
    if IntegrazioneconVitaminaD=='FALSE':IntegrazioneconVitaminaD='No' 
    else: IntegrazioneconVitaminaD='Si'
    Problemisegnalatidaigenitori=rec[fields['Problemisegnalatidaigenitori']]
    EventualiRilievi=rec[fields['EventualiRilievi']]
    Sintesidellosservazione=rec[fields['Sintesidellosservazione']]
    Suggerimenti=rec[fields['Suggerimenti']]
    DatadiNascita=rec[fields['[Pazienti].[DatadiNascita]']]
    dn=parseDate(DatadiNascita)
    DatadiNascita=dn.strftime('%d/%m/%Y')
    LuogodiNascita=rec[fields['[Pazienti].[LuogodiNascita]']]
    Tipodivisita=rec[fields['[Tipivisite].[Tipodivisita] as tp']]
    TipodivisitaID=rec[fields["[Visite].Tipodivisita"]]
    totw=700
    if Edit:
        fields1a={'Cognome/Nome':Cognome+' '+Nome,'CH:DataNascita|Data di Nascita':DatadiNascita,
        'Luogo di Nascita':LuogodiNascita,'CH:Sesso|Sesso':Sesso}
        fields1b={'CH:currentCodPaz|Codice Paziente':Paziente,'CH:currentCodVisita|Codice Visita':codVisita}
        tp,optionsTipiVis=getListaTipiVisite()
        fields2={'DRP:Tipodivisita|Tipo Visita|'+optionsTipiVis:TipodivisitaID,
                 'INP:MotivodellaVisita|Motivo della visita':MotivodellaVisita,
                 'DAT:DataVisita|Data della visita':dataVisita,
                 'INP:PesoRilevato(gr)|Peso rilevato (gr)':PesoRilevato_gr,
                 'INP:Lunghezza(cm)|Lunghezza (cm)':Lunghezza,
                 'INP:CirconferenzaCranica|Circ. cranica (cm)':CirconferenzaCranica
             }    

        fields4={'RAD:LatteMaterno|Latte Materno|Si,No':LatteMaterno,
                 'RAD:AltroLatte|Altro Latte|Si,No':AltroLatte,                 
                 'RAD:IntegrazioneconVitaminaD|Integrazione con Vitamina D|Si,No':IntegrazioneconVitaminaD,
                 'ETX:TipodiLatte|Dieta Alimentare':TipodiLatte}
                 
        fields5={'ETX:Problemisegnalatidaigenitori|Problemi segnalati dai genitori':Problemisegnalatidaigenitori,
                 'ETX:EventualiRilievi|Eventuali Rilievi':EventualiRilievi,
                 'ETX:Sintesidellosservazione|Sintesi dell\'osservazione':Sintesidellosservazione,
                 'ETX:Suggerimenti|=':Suggerimenti}
    else:
        fields1a={'Cognome/Nome':Cognome+' '+Nome,'Data di Nascita':DatadiNascita,
        'Luogo di Nascita':LuogodiNascita}
        fields1b={'CH:currentCodPaz|Codice Paziente':Paziente,
                  'CH:currentCodVisita|Codice Visita':codVisita,
                  'Sesso':Sesso,
                  }

    
        fields2={'Tipo Visita':Tipodivisita,'Motivo della visita':MotivodellaVisita,
                 'Data della visita':dataVisita,'Eta\'':eta,
                 #}
        #fields3={
                'Peso rilevato (gr/%)':peso_P,'Lunghezza (cm/%)':lung_P,
                 'Circ. cranica (cm/%)':circ_P
             }    

        fields4={'LatteMaterno|Latte Materno':LatteMaterno,
                 'AltroLatte|Altro Latte':AltroLatte,                       
                 'IntegrazioneconVitaminaD|Integrazione con Vitamina D':IntegrazioneconVitaminaD,
                 'TX:Dieta Alimentare':TipodiLatte}
        fields5={'TX:Problemi segnalati dai genitori':Problemisegnalatidaigenitori,
                 'TX:Eventuali Rilievi':EventualiRilievi,
                 'TX:Sintesi dell\'osservazione':Sintesidellosservazione,
                 'TX:Suggerimenti':Suggerimenti}
    
    tab1a=creatab(fields1a,1,totw,mode)
    tab1b=creatab(fields1b,1,totw,mode)
    tab2=creatab(fields2,1,totw,mode)
    tab4=creatab(fields4,1,totw,mode)
    tab5=creatab(fields5,2,totw,mode)
    if mode=='HTML':
        tab='<TABLE><TR><TD style="vertical-align:top;">'+tab1a+'</TD><TD style="vertical-align:top;">'+tab1b+'</TD></TR>'
        tab +='<TR><TD style="vertical-align:top;">'+tab2+'</TD><TD style="vertical-align:top;">'+tab4+'</TD></TR>'
        tab +='<TR><TD style="vertical-align:top;" colspan=2>'+tab5+'</TD></TR>'
        tab +='</TABLE>'
        
    else:
        tab=html.Table([
            html.Tr([html.Td(tab1a,style={'vertical-align':'top','width':format(totw/2)+'px'}),
                     html.Td(tab1b,style={'vertical-align':'top','width':format(totw/2)+'px'})]),

            html.Tr([html.Td(tab2,style={'vertical-align':'top','width':format(totw/2)+'px'}),
                     html.Td(tab4,style={'vertical-align':'top','width':format(totw/2)+'px'})]),
            #html.Tr(html.Td(tab3,style={'vertical-align':'top','width':format(totw/2)+'px'})),
            html.Tr(html.Td(tab5,colSpan=2,style={'vertical-align':'top','width':format(totw)+'px'}))
        ])
    db.close()
    return tab,Paziente,email,dataVisita,nomeCognome

def get_emailBlock(to,cc,bcc,subject,body,attachment):
    buttonStyle= {'background-color': 'navy','color':   'white'}
    layout=html.Table([html.Tr([html.Td('To',style=tds(100)),html.Td(dcc.Input(to,id='emailTo',style={'width':'100%'}),style=tds(400))]),
                       html.Tr([html.Td('Cc',style=tds(100)),html.Td(dcc.Input(cc,id='emailCc',style={'width':'100%'}),style=tds(400))]),
                       html.Tr([html.Td('Bcc',style=tds(100)),html.Td(dcc.Input(bcc,id='emailBcc',style={'width':'100%'}),style=tds(400))]),
                       html.Tr([html.Td('Subj',style=tds(100)),html.Td(dcc.Input(subject,id='emailSubject',style={'width':'100%'}),style=tds(400))]),
                       html.Tr([html.Td(dcc.Textarea(value=body,id='emailBody',style={'height':'200px','width':'100%'})
                                        ,colSpan=2)]),
                       html.Tr([html.Td('att',style=tds(100)),html.Td(attachment,id='outFilePDF',style=tds(400))]),
                       html.Tr([html.Td('',colSpan=2,id='logEmail')]),
                       html.Tr([html.Td(''),html.Td([html.Button('Invia',id='btnSendEmail',style=buttonStyle),
                                                     html.Button('Chiudi',id='btnCloseEmail',style=buttonStyle)
                                                     ],style={'text-align':'right'})])
                       ]
                      ,style={'background-color':'rgb(174, 214, 241)'})
    return layout

def showVisita(userID,codVisita,codPaz='',role='',modeHeader='',url='',emailID='',nomeCognomeID=''):
    print(userID,codVisita,codPaz,'role='+role+'<<<')
    if codVisita=='NEW' and codPaz !='' and role=='':
        tab,codPaz,email,dataVisita,nomeCognome=creaTabVisita(userID,codVisita,True,codPaz)
        edits=html.Td([ html.Button('<',id='butPrev',disabled=True,style={'background-color':'lightGray'}),
                    html.Button('>',id='butNext',disabled=True,style={'background-color':'lightGray'}),
                    html.Button('Nuova Visita',id='NewVis',disabled=True,style={'background-color':'lightGray'}),
                    html.Button('Modifica',id='EditVis',disabled=True,style={'background-color':'lightGray'}),                    
                    html.Button('Salva',id='SaveVis'),                                       
                    html.Button('Elimina',id='DeleteVis',disabled=True,style={'background-color':'lightGray'}),
                    html.Button('Chiudi',id='ChiudiVis'),
                   ]
                  )
        grafs=''
    else:
        print('sono qui xxxx',role,role=='utente')
        tab,codPaz,email,dataVisita,nomeCognome=creaTabVisita(userID,codVisita,'','',modeHeader)
        idenc=EncUsPw(codVisita,userID,codPaz)  
        print(url)
        #url=url.split('/showVisita')[0]
        linkPrint=url+'/showVisita?enc='+idenc
        body='Scheda Visita Medica\n\nIn allegato la visita effettuata a:'+nomeCognome+' in data '+dataVisita+'\n\n'+nomeCognomeID

        emailBlock=get_emailBlock(email,emailID,'','[PEDIWEB] Visita dott.ssa Bonini',body,'')
        linkEmail='mailto:'+email+'?subject=[PEDIWEB] Scheda Visita&body=Visita Dott.ssa Bonini%0D%0A%0D%0ACliccare sul link o copiarlo e incollarlo in un browser:%0D%0A'+linkPrint
        edits=html.Td([ html.Button('<',id='butPrev'),
                    html.Button('>',id='butNext'),
                    html.Button('Nuova Visita',id='NewVis'),
                    html.Button('Modifica',id='EditVis'),
                    html.Button('Salva',id='SaveVis',disabled=True,style={'background-color':'lightGray'}), 
                    html.Button('Elimina',id='DeleteVis'),
                    html.Button('Chiudi',id='ChiudiVis'),                                       

                   ]
                  )
        if modeHeader=='print':
            grafs=pl.creaPlots(codPaz,codVisita,180,170,modeHeader)
        else:
            grafs=pl.creaPlots(codPaz,codVisita,800)

    dummy,options=getListaVisite(codPaz)
    
    divPlots=html.Div(grafs,id='plotsV')
    ckList=dcc.Dropdown(id='listaVisite',options=options,value=codVisita,style={'width':'150px','text-align':'center'})
    link=html.A('Torna alla scheda Paziente',href='/showSummary?id='+format(codPaz))
    controls=html.Table(html.Tr([html.Td('Seleziona una visita'),
                                 html.Td(ckList),edits
                                 ]
                                )
                        )
    currUser=html.Div(userID,id='currentUser')
    red=html.Div(id="hidden_div_for_redirect_callback")
    if role=='utente':
        controls=''
    if modeHeader=='print':
        listaVisite,dummy=getListaVisite(codPaz,5,'print')
        layout=html.Center([Navbar(modeHeader,userID),
                            html.Table([html.Tr([html.Td(html.Div([tab],id='dettVisita'),style=tds(600)),
                                                 html.Td(divPlots,style=tds(200))
                                                ]),
                                       html.Tr(html.Td([html.B('Lista ultime 5 visite'),html.Br(),listaVisite],colSpan=2,style=tds(700)
                                                       )
                                               )]
                                       )
                                       
                            ,currUser])
    else:
        link='/get_visita?codeVisita='+format(codVisita)
        bottoniera=html.Div([
                    html.A(html.Img(src=srcPrintImg,style={'width':'30px'}),id='btnPrint',href=link,target='_new'),
                    html.Button(html.Img(src=srcPDFImg,style={'width':'30px'}),id='btnDownloadPDF'),
                    html.Button(html.Img(src=srcEmailImg,style={'width':'30px'}),id='btnCreateEmail')
                    ])
        layout=html.Center([red,Navbar(modeHeader,userID),
                    
                            html.Div(emailBlock,id='emailBlock',style={'display':'none'}),
                            dcc.Download(id="download-pdf"),
                            html.Br(),
                            bottoniera,html.Br(),
                            dcc.Loading(id="loading",children=[html.Div([html.Div(id="loading-output")])],type="circle",),
                            controls,html.Div(tab,id='dettVisita'),divPlots,currUser])
    return layout
    
  

def getListaVisite(codice,Nmax='',mode=''):
    db=dbase(dbname)

    fields={'DataVisita':0,'[Eta(anni/mesi/giorni)]':1,'[tipiVisite].[Tipodivisita] as tp':2,'MotivodellaVisita':3,
            'Visite.CodiceVisita':4}
    sql='SELECT '
    sql +=','.join(fields.keys())
    sql+=' from Visite LEFT JOIN [tipiVisite] ON Visite.[Tipodivisita] = [tipiVisite].[CodiceVisita] WHERE [Paziente]='
    sql+= format(codice) +' and (LOWER([deleted])=\'false\' or [deleted] is Null)'
    sql+=' order by [dataVisita] desc'
    #print(sql)
    records=db.getRecord(sql)
    listRec=[]
    options=[]
    if Nmax=='':
        Nmax=len(records)
    for rec in records[:Nmax]:
        #print('dv',rec[fields['DataVisita']])
        dataVisita=parseDate(rec[fields['DataVisita']])
        listRec.append([dataVisita,rec])
    listRec.sort(reverse=True)
    #rec=db.getTableRecord('Visite','Paziente='+format(codice))
    rows=[]
    rowsHTML=[]
    td=tds('','',12,'light-gray','','navy')
    for recL in listRec:
        rec=recL[1]
        dataVisita=parseDate(rec[fields['DataVisita']]).strftime('%d/%m/%Y')
        eta=rec[fields['[Eta(anni/mesi/giorni)]']]
        tp=rec[fields['[tipiVisite].[Tipodivisita] as tp']]
        motivo=rec[fields['MotivodellaVisita']]
        codVisita=rec[fields['Visite.CodiceVisita']]
        options.append({'label':dataVisita,'value':codVisita})
        if mode=='':
            link=html.A('Apri visita',href='/showVisita?id='+format(codVisita))
        else:
            link=''
        rows.append(html.Tr([html.Td(dataVisita,style=tds(200)),html.Td(eta,style=tds(200)),
                             html.Td(tp,style=tds(200)),html.Td(motivo,style=tds(400)), html.Td(link,style=tds(100))]))
        rowHTML='<TR><TD class="lv">'+dataVisita+'</TD>'
        rowHTML+='<TD class="lv">'+eta+'</TD>'
        rowHTML+='<TD class="lv">'+fnull(tp)+'</TD>'
        rowHTML+='<TD class="lv">'+motivo+'</TD></TR>'
        rowsHTML.append(rowHTML)
    if mode !='HTML':
        tab=html.Center(html.Table(rows))
    else:
        tab='<TABLE>'+'\n'.join(rowsHTML)+'</TABLE>'
    
    db.close()
    return tab,options

def getLista(userID,selPaz=[]):
    db=dbase(dbname)
    sql='SELECT Codicepaziente,Cognome,Nome,DatadiNascita from Pazienti where ([Deleted]=\'False\' or [Deleted] is Null) and userID='+format(userID)+' order by LOWER(Cognome),LOWER(Nome)'
    #print(sql)
    paz=db.getRecord(sql) #  WHERE  Cognome like "Annunziato"')
    options=[]
    for p in paz:
        Codicepaziente,Cognome,Nome,DatadiNascita=p
        #print(DatadiNascita)
        dn=parseDate(DatadiNascita)
        #print('dn=',dn)
        options.append({'label':Cognome+' '+Nome+' ('+format(dn.year)+')','value':Codicepaziente})
    
    selectPaziente=dcc.Dropdown(id='listaPazienti',options=options,value=selPaz,style={'font-size':'20px'})
    db.close()
    return selectPaziente,options

def getScheda(userID,codice, Edit=False):
    #'LuogodiNascita': 6, 'Abitazione:via': 7, 'Comune': 8, 'Provincia': 9, 'CAP': 10, 
    #'Telefono': 11, 'Padre': 12, 'Madre': 13, 'AnamnesiFamiliare': 14, 
    #'CodiceVaccinazione1': 15, 'Vaccinazione1': 16, 'NoteVaccinazione1': 17,
    # 'CodiceVaccinazione2': 18, 'Vaccinazione2': 19, 'NoteVaccinazione2': 20, 'CodiceVaccinazione3': 
    # 21, 'Vaccinazione3': 22, 'NoteVaccinazione3': 23, 'CodiceVaccinazione4': 24, 'Vaccinazione4': 25, 
    # 'NoteVaccinazione4': 26, 'CodiceVaccinazione5': 27, 'Vaccinazione5': 28, 'NoteVaccinazione5': 29,
    #  'CodiceVaccinazione6': 30, 'Vaccinazione6': 31, 'NoteVaccinazione6': 32, 'CodiceVaccinazione7': 33, 
    #  'Vaccinazione7': 34, 'NoteVaccinazione7': 35, 'CodiceVaccinazione8': 36, 'Vaccinazione8': 37, 
    #  'NoteVaccinazione8': 38, 'CodiceVaccinazione9': 39, 'Vaccinazione9': 40, 'NoteVaccinazione9': 41, 'CodiceVaccinazione10': 42, 'Vaccinazione10': 43, 'NoteVaccinazione10': 44, 'CodiceVaccinazione11': 45, 'Vaccinazione11': 46, 'NoteVaccinazione11': 47, 'CodiceVaccinazione12': 48, 'Vaccinazione12': 49, 'NoteVaccinazione12': 50, 'CodiceVaccinazione13': 51, 'Vaccinazione13': 52, 'NoteVaccinazione13': 53, 'CodiceVaccinazione14': 54, 'Vaccinazione14': 55, 'NoteVaccinazione14': 56, 'CodiceVaccinazione15': 57, 'Vaccinazione15': 58, 'NoteVaccinazione15': 59, 'CodiceVaccinazione16': 60, 'Vaccinazione16': 61, 'NoteVaccinazione16': 62, 'CodiceVaccinazione17': 63, 'Vaccinazione17': 64, 'NoteVaccinazione17': 65, 'CodiceOriginale': 66, 'ArchivioOriginale': 67, 'Deleted': 68}
    db=dbase(dbname)
    if not codice=='NEW':
        
        rec=db.getTableRecord('Pazienti','userID='+format(userID)+' and CodicePaziente='+format(codice))
        if len(rec)>0:
            rec=rec[0]
        else:
            #print('userID='+format(userID)+' and CodicePaziente='+format(codice))
            return 'no record found'
        Cognome=        rec['Cognome']
        Nome=           rec['Nome']
        via=            fnull(rec['Via'])
        Comune=         fnull(rec['Comune'])
        Prov=           fnull(rec['Provincia'])
        CAP=            fnull(rec['CAP'])
        IndirizzoCompleto=via+', '+format(CAP)+' '+Comune+' ('+Prov+')'
        Sesso   =       rec['Sesso']
        Telefono=       fnull(rec['Telefono'])
        cellulare=       fnull(rec['Cellulare'])
        email=           fnull(rec['email'])
        Vaccinazioni=    fnull(rec['Vaccinazioni'])
        DatadiNascita=  parseDate(rec['DatadiNascita']).strftime('%d/%m/%Y')
        LuogodiNascita=  rec['LuogodiNascita']
        Padre=fnull(rec['Padre'])
        Madre=fnull(rec['Madre'])
        anam=fnull(rec['AnamnesiFamiliare'])
        dn=parseDate(DatadiNascita)
        eta=CalcolaEta(dn,datetime.utcnow())
    else:
        Cognome=        ""
        Nome=           ""
        via=            ""
        Comune=         ""
        Prov=           ""
        CAP=            ""
        IndirizzoCompleto=via+', '+format(CAP)+' '+Comune+' ('+Prov+')'
        Sesso   =       ""
        Telefono=       ""
        DatadiNascita=  datetime.utcnow().strftime('%d/%m/%Y')
        LuogodiNascita=  ""
        Sesso=""
        Padre=""
        Madre=""
        anam=""
        email='';cellulare='';Vaccinazioni=''
        dn=datetime.utcnow()
        eta=CalcolaEta(dn,datetime.utcnow())

    totw=700
    if Edit:
        fields1={'INP:Cognome|=':Cognome,'INP:Nome|=':Nome,'INP:Via|=':via,'INP:CAP|=':CAP,
                 'INP:Comune|=':Comune,'INP:Provincia|=':Prov,'INP:Telefono|=':Telefono,'INP:Cellulare|Cellulare':cellulare,
                 'INP:email|Email@':email}
        fields2={'INP:LuogodiNascita|Luogo di Nascita':LuogodiNascita,
                 'DAT:DatadiNascita|Data di Nascita':DatadiNascita,'RAD:Sesso|=|M,F':Sesso,                 
                 'ETX:Vaccinazioni|Vaccinzioni':Vaccinazioni}
        fields3={'INP:Padre|=':Padre,'INP:Madre|=':Madre}
        fields3a={'ETX:AnamnesiFamiliare|Anamnesi Familiare':anam}
    else:
        fields1={'Cognome|=':Cognome,'Nome|=':Nome,'Indirizzo|=':IndirizzoCompleto,'Telefono|=':Telefono,
                 'Cellulare':cellulare,'Email@':email}
        fields2={'LuogodiNascita|Luogo di Nascita':LuogodiNascita,
                 'DatadiNascita|Data di Nascita':DatadiNascita,'Eta\'':eta,
                 'Sesso|=':Sesso,'TX:Vaccinazioni|Vaccinazioni':Vaccinazioni}
        fields3={'Padre|=':Padre,'Madre|=':Madre}
        fields3a={'TX:AnamnesiFamiliare|Anamnesi Familiare':anam}


    tab1=creatab(fields1)
    tab2=creatab(fields2)
    tab3=creatab(fields3,1,totw)
    tab3a=creatab(fields3a,1,totw)
    if codice=='NEW':
        tab4=''
    else:
        tab4,dummy=getListaVisite(codice)
    link=html.A(['Crea una ',
                 html.B('Nuova'),
                 ' visita'],href='/showVisita?id=NEW&idPaz='+format(codice))
    tab=html.Table([html.Tr([html.Td(tab1,style={'width':format(totw/2)+'px','vertical-align':'top'}),
                             html.Td(tab2,style={'width':format(totw/2)+'px','vertical-align':'top'})
                             ]),
                    html.Tr(html.Td(tab3,style={'width':format(totw)+'px'},colSpan=2)),
                    html.Tr(html.Td(tab3a,style={'width':format(totw)+'px'},colSpan=2)),                    
                    html.Tr(html.Td([html.H4('Lista Visite'),link,html.Br(),tab4],style={'width':format(totw)+'px','text-align':'center'},colSpan=2))
                    ]
                    )
    #tab=html.Div([tabs,tabContent])
    #print(tabs)
    db.close()
    return tab


def schedaPaziente(userID,codicePaziente='',Edit=False,Selected=False):    
    selectPaziente,dummy=getLista(userID,codicePaziente)
    if Selected:
        edits=html.Td([ html.Button('Nuovo',id='NewPaz',disabled=True,style={'background-color':'lightGray'}),
                    html.Button('Modifica',id='EditPaz'),
                    html.Button('Salva',id='SavePaz',disabled=True,style={'background-color':'lightGray'}),                                       
                    html.Button('Elimina',id='DeletePaz'),
                    html.Button('Chiudi',id='ChiudiPaz'),
                   ]
                  )
        selected=codicePaziente
    else:
        edits=html.Td([ html.Button('Nuovo Paz',id='NewPaz'),
                    html.Button('Modifica',id='EditPaz',disabled=True,style={'background-color':'lightGray'}),
                    html.Button('Salva',id='SavePaz',disabled=True,style={'background-color':'lightGray'}),  
                    html.Button('Elimina',id='DeletePaz',disabled=True,style={'background-color':'lightGray'}),                                       
                    html.Button('Chiudi',id='ChiudiPaz',disabled=True,style={'background-color':'lightGray'})                    
                   ]
                  )
        selected=''               
                       
    controls=html.Table([html.Tr(html.Td('Seleziona un paziente o creane uno nuovo',colSpan=2)),
                         html.Tr([html.Td(selectPaziente,style={'width':'400px'}),edits])]
                        )
    scheda='';tc='';grafs=''
    scheda=html.Div(id='Anamnesi')
    
    if codicePaziente !='':
        scheda=getScheda(userID,codicePaziente,Edit)
        grafs=pl.creaPlots(codicePaziente)
    divScheda=html.Div(scheda,id='scheda')
    divPlots=html.Div(grafs,id='plots')
    divCurrentUser=html.Div(userID,id='currentUser')
    statLine=html.Div(id='statusLine')
    divCurrentCodice=html.Div(codicePaziente,id='currentCodice')
    
    layout=html.Center([Navbar(),statLine,controls,divScheda,divCurrentUser,divCurrentCodice,divPlots])
    return layout

@app.callback(Output('scheda','children'), Output('plots','children'),              
              Output('currentCodice','children'),
              Output('statusLine','children'),
              Output('listaPazienti','value'),

              Output('EditPaz','style'),
              Output('NewPaz','style'),
              Output('SavePaz','style'),
              Output('DeletePaz','style'),
              Output('ChiudiPaz','style'),

              Output('EditPaz','disabled'),
              Output('NewPaz','disabled'),              
              Output('SavePaz','disabled'),
              Output('DeletePaz','disabled'),
              Output('ChiudiPaz','disabled'),
              Output('listaPazienti','options'),
                           
              Input('listaPazienti','value'),
              Input('EditPaz','n_clicks'),
              Input('SavePaz','n_clicks'),
              Input('DeletePaz','n_clicks'),
              Input('NewPaz','n_clicks'),
              Input('ChiudiPaz','n_clicks'),

              State('scheda','children'),
              State('currentUser','children'),              
              State('currentCodice','children'),
              State('listaPazienti','options'),
              prevent_initial_call=True)

def clickedPaziente(selPaz,btnsave,btnedit,btnDel,btnNew,btnChiudi,scheda,userID,currentCodice,listaPaz):
    evID=ctx.triggered_id
    print('PID=',os.getpid())
    db=dbase(dbname)
    #print('evID=',evID,selPaz)
    show={'background-color':'white'}
    hide={'background-color':'LightGray'}
    showE=False
    hideE=True
    buts=[hide,show,hide,hide,hide,  hideE,showE,hideE,hideE,hideE]

    if evID=='listaPazienti':
        if selPaz==[] or selPaz==None:                                   #Edit Nuovo Sal Chiu
            return ['','','Seleziona un paziente dalla lista o crea nuovo',selPaz,'']+buts+[listaPaz]
            #return ['','','','','']+buts+[listaPaz]
        codice=selPaz
        #print('clickedPaziente',userID,codice)
        scheda=getScheda(userID,codice)
        grafs=pl.creaPlots(codice)
                                             #Edit Nuovo Sal Chiu
        buts=[show,hide,hide,show,show,  showE,hideE,hideE,showE,showE]
        return [scheda,grafs,codice,'',selPaz]+buts+[listaPaz]
    elif evID=='DeletePaz':
        sql='UPDATE Pazienti set [Deleted]=\'True\' where CodicePaziente='+format(currentCodice)
        db.execSQL(sql)
        sql='UPDATE Visite set [Deleted]=\'True\' where Paziente='+format(currentCodice)
        db.execSQL(sql)

        dummy,listaPaz=getLista(userID)
        buts=[hide,show,hide,hide,hide,  hideE,showE,hideE,hideE,hideE]
        return ['','','','Paziente eliminato. Se cancellato per errore rivolgersi ad A.A.',selPaz]+buts+[listaPaz]

    elif evID=='EditPaz':
        codice=currentCodice
        #print('ridefinisco scheda con Edit=True')
        scheda=getScheda(userID,codice,True)
        buts=[hide,hide,show,hide,show,  hideE,hideE,showE,hideE,showE]
        print(buts)
        return [scheda,'',codice,'',selPaz]+buts+[listaPaz]
    elif evID=='NewPaz':
        codice="NEW"
        scheda=getScheda(userID,codice,True)
        db.close()
        buts=[hide,hide,show,hide,show,  hideE,hideE,showE,hideE,showE]
        return [scheda,'',codice,'',selPaz]+buts+[listaPaz]

    elif evID=='ChiudiPaz':
                       #Edit Nuovo Sal Chiu
        db.close()
        buts=[hide,show,hide,hide,hide,  hideE,showE,hideE,hideE,hideE]
        return ['','','','','']+buts+[listaPaz]
    elif evID=='SavePaz':
        currentCodice0=currentCodice
        if currentCodice=='NEW':
            sql="INSERT INTO Pazienti (Nome,userID) VALUES ('',"+format(userID)+")"
            db.execSQL(sql)
            rec=db.getRecord('select CodicePaziente from Pazienti order by CodicePaziente desc limit 1')
            currentCodice=rec[0][0]
        fields=['Cognome','Nome','Via','CAP','Comune','Provincia','Telefono',
                 'LuogodiNascita','DatadiNascita','Sesso','Cellulare','email','Vaccinazioni',
                 'Padre','Madre','AnamnesiFamiliare']
        sql='update Pazienti set '
        fie='[Deleted]=\'False\''
        for f in fields:
            if not fie =='':
                fie +=','
                #print(fie)
            p=getpath(scheda,'id',f)
            if p != None:                
                if 'date' in p:
                    if 'T' in p['date']:
                        value=datetime.strptime(p['date'],'%Y-%m-%dT00:00:00').strftime('%d/%m/%Y 00:00')
                    else:
                        value=datetime.strptime(p['date'],'%Y-%m-%d').strftime('%d/%m/%Y 00:00')
                elif 'value' in p:
                    value=p['value']
                else:
                    value=p
                if format(value)=='None':
                    value=''
                fie +='['+f+"]='"+format(value)+"'"
                #print(f,value)
           
        sql +=fie + ' WHERE CodicePaziente=' + format(currentCodice)
        #print(sql)
        ret=db.execSQL(sql)
        if currentCodice0=='NEW':
            dummy,listaPaz=getLista(userID)
        #print('ret=',ret)
        #  salva tutto
        # saveScheda(scheda)
        codice=currentCodice
        scheda=getScheda(userID,currentCodice,False)
        grafs=pl.creaPlots(currentCodice)
        db.close()                                               #Edit Nuovo Sal Chiu
        buts=[show,hide,hide,show,show,  showE,hideE,hideE,showE,showE]
        return [scheda,grafs,codice,'Salvato record',currentCodice]+buts+[listaPaz]



def givenew(lista,currValue,dire):
    for k in range(len(lista)):
        elem=lista[k]
        lab=elem['value']
        if format(lab)==format(currValue):
            if dire==1:
                if k<len(lista)-1:
                    return lista[k+1]['value']
            elif dire==-1:
                if k>0:
                    return lista[k-1]['value']
    return currValue
        
@app.callback(Output('dettVisita','children'), Output('plotsV','children'),              
              Output('listaVisite','value'),

              Output('EditVis','style'),
              Output('NewVis','style'),
              Output('SaveVis','style'),
              Output('DeleteVis','style'),
              Output('ChiudiVis','style'),

              Output('EditVis','disabled'),
              Output('NewVis','disabled'),
              Output('SaveVis','disabled'),
              Output('DeleteVis','disabled'),
              Output('ChiudiVis','disabled'),
              Output('hidden_div_for_redirect_callback','children'),
                           
              Input('listaVisite','value'),
              Input('butNext','n_clicks'),
              Input('butPrev','n_clicks'),
              Input('EditVis','n_clicks'),
              Input('SaveVis','n_clicks'),
              Input('DeleteVis','n_clicks'),
              Input('NewVis','n_clicks'),
              Input('ChiudiVis','n_clicks'),

              State('dettVisita','children'),
              State('listaVisite','options'),
              State('currentCodPaz','children'),
              State('currentCodVisita','children'),
              State('currentUser','children'),
              prevent_initial_call=True)

def updateVisita(newcod,clickNext,clickPrev,clE,clSa,clDe,clNew,clChi,scheda,lv,currCodPaz,currCodVisita,userID):
    evID=ctx.triggered_id
    #print(evID)
    print('PID=',os.getpid())
    scod=''
    edit=False
    enab={'background-color':'white'}
    disab={'background-color':'LightGray'}
    enabE=False
    disabE=True
    buts=[enab,enab,disab,disab,enab, enabE,enabE,disabE,disabE,enabE]
    if evID=='butPrev':
        currCodVisita=givenew(lv,currCodVisita,-1)        
    elif evID=='butNext':
        currCodVisita=givenew(lv,currCodVisita,+1)
    elif evID=='EditVis':
        edit=True
        buts=[disab,disab,enab,disab,enab, disabE,disabE,enabE,disabE,enabE]
    elif evID=='DeleteVis':
        sql='UPDATE Visite set deleted=\'True\' where Codicevisita='+format(currCodVisita)
        db=dbase(dbname)
        print(' DELETE\n\n'+sql)
        db.execSQL(sql)
        db.close()
        return ['','','']+buts+[dcc.Location(pathname="/showSummary/"+format(currCodPaz), id="someid_doesnt_matter")]
    elif evID=='ChiudiVis':
        return ['','','']+buts+[dcc.Location(pathname="/showSummary/"+format(currCodPaz), id="someid_doesnt_matter")]
    elif evID=='NewVis':
        codice="NEW"
        currCodVisita=codice
        edit=True
        scod=currCodPaz
        buts=[disab,disab,enab,enab,True,True,False,False]        
    elif evID=='SaveVis':
        try:
            db=dbase(dbname)
            edit=False
            currCodVisita0=currCodVisita
            if currCodVisita=='NEW':
                sql="INSERT INTO Visite (Paziente,userID) VALUES ("+format(currCodPaz)+","+format(userID)+")"
                #print(sql)
                db.execSQL(sql)
                rec=db.getRecord('select CodiceVisita from Visite order by CodiceVisita desc limit 1')
                currCodVisita=rec[0][0]
                #print('new code visita=',currCodVisita)
            fields=['Paziente','Tipodivisita','MotivodellaVisita','DataVisita','PesoRilevato(gr)',
                     'Lunghezza(cm)','CirconferenzaCranica','LatteMaterno','AltroLatte','IntegrazioneconVitaminaD',
                     'Problemisegnalatidaigenitori','EventualiRilievi','Sintesidellosservazione',
                     'Suggerimenti','TipodiLatte']
            sql='update Visite set '
            #with open('scheda.json','w') as f:
            #    f.write(json.dumps(scheda))
            fie=''
            for f in fields:
                if not fie =='':
                    fie +=','
                    #print(fie)
                p=getpath(scheda,'id',f)
                if p != None:                
                    if 'date' in p:
                        print('p,p[date]',p,p['date'])
                        value=parseDate(p['date'])
                        #value=datetime.strptime(p['date'],'%Y-%m-%dT00:00:00').strftime('%d/%m/%Y 00:00')
                    elif 'value' in p:
                        value=p['value']
                    else:
                        value=p
                    if format(value)=='None':
                        value=''
                    if f in ['LatteMaterno','AltroLatte','IntegrazioneconVitaminaD']:
                        #print(f,p,value)                    
                        if value=='No':
                            value='FALSE'
                        else:
                            value='TRUE'
                    fie +='['+f+"]='"+format(value).replace("'","''")+"'"
                    #print(f,value)
                    if f in ['DataVisita','PesoRilevato(gr)','CirconferenzaCranica','Lunghezza(cm)']:
                        dnS=getpath(scheda,'id','DataNascita')['children']
                        Sesso=getpath(scheda,'id','Sesso')['children']
                        dn=parseDate(dnS)
                        dvS=getpath(scheda,'id','DataVisita')['date']
                        dv=parseDate(dvS)
                        etamesi=CalcolaEta(dn,dv,True)
                        if f=='DataVisita':                        
                            eta=CalcolaEta(dn,dv)
                            fie +=',[Eta(anni/mesi/giorni)]=\''+eta+'\''
                        elif f=='PesoRilevato(gr)':                                                                        
                            perc=ValutaPerc(value, 'Peso', Sesso, etamesi)
                            #print('Peso',value,'%',perc)
                            fie +=',[Peso_percentile]=\''+format(perc)+'\''
                        elif f=='Lunghezza(cm)':
                            perc=ValutaPerc(value, 'Statura', Sesso, etamesi)
                            fie +=',[Lunghezza_percentile]=\''+format(perc)+'\''
                            #print('Statura',value,'%',perc)
                        elif f=='CirconferenzaCranica':
                            perc=ValutaPerc(value, 'CircCran', Sesso, etamesi)
                            fie +=',[Circonferenza_percentile]=\''+format(perc)+'\''
                            #print('CircCran',value,'%',perc)
                    
            sql +=fie + ' WHERE CodiceVisita=' + format(currCodVisita)
#            print(sql)        
            ret=db.execSQL(sql)
            db.close()
            #if currCodVisita0=='NEW':
            #    dummy,listaPaz=getLista(userID)
        
            buts=[enab,enab,disab,disab,enab,  enabE,enabE,disabE,disabE,enabE]
        except Exception as e:
            return [' Error '+format(e),'','']+buts+['']
    tab,options,emai,dataVisita,nomeCognomel=creaTabVisita(userID,currCodVisita,edit,scod)
    grafs=pl.creaPlots(currCodPaz,currCodVisita)
    print('PID=',os.getpid())
    return [tab,grafs,currCodVisita]+buts+['']

def creaPDF(userID,codVisita,onlyHTML=False):
        tab,codPaz,email,dataVisita,nomeCognome=creaTabVisita(userID,codVisita,'','','HTML')
        
    #     linkEmail='mailto:'+email+'?subject=[PEDIWEB] Scheda Visita&body=Visita Dott.ssa Bonini%0D%0A%0D%0ACliccare sul link o copiarlo e incollarlo in un browser:%0D%0A'+linkPrint
        
        grafs=pl.creaPlots(codPaz,codVisita,180,170,'HTML')
        tabgraf='<TABLE>'
        for j in range(3):
            outFile=SAVEDIR+os.sep+'_temp'+os.sep+'visita_'+format(codVisita)+'_fig'+format(j)+'.png'
            grafs[j].write_image(outFile)
            tabgraf +='<TR><TD><IMG src="'+outFile+'"></TD></TR>'
        tabgraf +='</TABLE>'
        dummy,options=getListaVisite(codPaz)
    
        currUser=html.Div(userID,id='currentUser')
        red=html.Div(id="hidden_div_for_redirect_callback")
        listaVisite,dummy=getListaVisite(codPaz,5,'HTML')
        stile='<style>'
        stile +='body {font-family:Arial;}'
        stile +='.label {background-color:lightgray;border: 1px black solid;width:120}'
        stile +='.value {font-weight:bold;border: 1px black solid;width:180;height:40;vertical-align: top;}'
        stile +='.label2 {background-color:lightgray;border: 1px black solid;width:300}'
        stile +='.value2 {font-weight:bold;border: 1px black solid;width:300;height:100;vertical-align: top;}'
        stile +='.lv {width:200;border-bottom: 1px black solid;vertical-align:top}'
                         
        
        stile+='</style>'
        layout='<HTML><HEAD>'+stile+'</HEAD><BODY style="font-face:Arial;"><CENTER>'+Navbar('HTML',userID)
        layout +='<TABLE><TR><TD>'+tab+'</TD><TD style="vertical-align:top;width:200">'+tabgraf+'</TD></TABLE>'
        layout +='<B>Lista ultime 5 visite</B><BR>'+listaVisite
        layout +='</BODY></HTML>'
        outFile=SAVEDIR+os.sep+'_temp'+os.sep+'visita_'+format(codVisita)+'.html'
        outFilePDF=SAVEDIR+os.sep+'_temp'+os.sep+'visita_'+format(codVisita)+'.pdf'
        with open(outFile,'w',encoding='utf-8') as f:
            f.write(layout)
        if onlyHTML:
            return outFile
        else:
            printLog('ora cancello il pdf',outFilePDF)
            if os.path.exists(outFilePDF):
                        os.remove(outFilePDF)
            printLog('cancellato')
            path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf) 
            pdfkit.from_file(outFile,outFilePDF, configuration=config, options={"enable-local-file-access": ""})
            printLog('out da pdfkit')
            os.remove(outFile)
            for j in range(3):
                outFile=SAVEDIR+os.sep+'_temp'+os.sep+'visita_'+format(codVisita)+'_fig'+format(j)+'.png'
                os.remove(outFile)
    
            return outFilePDF

@app.callback(Output("loading-output", "children"),
              
              Input('btnCreateEmail','n_clicks'),
              State('currentCodPaz','children'),
              State('currentCodVisita','children'),
              State('currentUser','children'), prevent_initial_call=True             
              )
def input_triggers_spinner(ncli,codPaz,codVisita,userID):
    printLog('sto per creare il pdf')
    outFilePDF=creaPDF(userID,codVisita)
    printLog('ho creato il pdf ',outFilePDF)
    return outFilePDF

@app.callback(Output('emailBlock','style'),
              Output('outFilePDF','children'),
              Output('logEmail','children'),
              Output('download-pdf','data'),

              Input('loading-output','children'),
              Input('btnSendEmail','n_clicks'),
              Input('btnCloseEmail','n_clicks'),
              Input('btnDownloadPDF','n_clicks'),
              #Input('btnPrint','n_clicks'),
              State('currentCodPaz','children'),
              State('currentCodVisita','children'),
              State('currentUser','children'),
              State('outFilePDF','children'),
              State('emailTo','value'),State('emailCc','value'),State('emailBcc','value'),State('emailSubject','value'),
              State('emailBody','value'),
              prevent_initial_call=True

              )

def createVisita_HTML(outFilePDF1,nclicks,nclickx1,nclicks2,codPaz,codVisita,userID,outFilePDF,
                      to,cc,bcc,subj,body):
    #  vanno installati:  pdfkit,  kaleido e wkhtmltopdf.exe
    # https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe
        printLog(codVisita,userID)
        evID=ctx.triggered_id
        printLog('evID=',evID)
        if evID=='btnDownloadPDF':
            printLog('vado a creare il PDF')
            outFilePDF=creaPDF(userID,codVisita)
            printLog('pdf creato ',outFilePDF,os.path.exists(outFilePDF))
            return {'display':'none'},'','',dcc.send_file(outFilePDF)
        #if evID=='btnPrint':
        #    outFileHTML=creaPDF(userID,codVisita,True)
        #    return {'display':'none'},'','',dcc.send_file(outFileHTML)

        elif evID=='btnCloseEmail':            
            return {'display':'none'},outFilePDF,'',None
        elif evID=='loading-output':
            printLog('dopo loading-output')
            return {'display':'block'},outFilePDF1,'',None
        elif evID=='btnSendEmail':
            outFilePDF=creaPDF(userID,codVisita)
            if os.path.exists(outFilePDF):            
                resp=upload(ftphost,ftpuser,ftpPass,SAVEDIR+os.sep+'_temp'+os.sep,ftpRemDir,'visita_'+format(codVisita)+'.pdf')
            else:
                resp='file pdf non esistente'
            print(outFilePDF)
            print(resp)
            if resp[0]==True:
                attachment='MAIL'+os.sep+'visita_'+format(codVisita)+'.pdf'
                sendMail(to,subj,body,cc,bcc,attachment)
                resp='Email inviata regolarmente'
            else:
                resp='errore nell invio della mail'
            return  {'display':'block'},outFilePDF,resp,None
        
