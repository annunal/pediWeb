from dashImport import *
from CONF import *
from utilities import *
import numpy as np

def showdatepicker():
    optDD=np.linspace(1,31,31)
    optMM=np.linspace(1,12,12)
    y0=datetime.utcnow().year
    optYY=np.linspace(1950,y0,y0-1950+1)
    dd=dcc.Dropdown(optDD,id='pick_DD',style={'width':'100%'})
    mm=dcc.Dropdown(optMM,id='pick_MM',style={'width':'100%'})
    yy=dcc.Dropdown(value=y0,options=optYY,id='pick_YY',style={'width':'100%'})
   

    dp=html.Table(html.Tr([
        html.Td(dd,style={'width':'80px','padding':'2px'}),
        html.Td(mm,style={'width':'80px','padding':'2px'}),
        html.Td(yy,style={'width':'100px','padding':'2px'})]
                          ))
    seldate=html.Div(id='seldate')
    return html.Div([dp,seldate])
def leapDays(year):
    if (year % 400) == 0:
        return 29
    elif (year % 100) != 0 and (year % 4) == 0:
        return 29
    else:
        return 28
@app.callback(Output('seldate','children'),
              Output('pick_DD','options'),
              Input('pick_DD','value'),
              Input('pick_MM','value'),
              Input('pick_YY','value'),
              State('pick_DD','options')
              )
def getdate(dd,mm,yy,opt):
    print(dd,mm,yy)
    if mm !='' and mm!=None and yy !='' and yy !=None:
        days=[0,31,leapDays(yy),31,30,31,30,31,31,30,31,30,31]
        opt=np.linspace(1,days[mm],days[mm])
    if mm !='' and dd!='' and yy !='' and mm !=None and dd!=None and yy !=None:
        dateSel=datetime(yy,mm,dd).strftime('%d/%m/%Y')
    else:
        dateSel='Seleziona giorno,mese e anno'
    return dateSel,opt
