import dbase
from dashImport import html,dcc
from CONF import dbname
from utilities import *
import plotly.graph_objects as go

class plots(object):
    """description of class"""


    def creaPlot(self,quant):
        fig = go.Figure()
        ht="<br>".join([
            "data: %{x}",
            quant+": %{y}",
            #"eta: %{name}"
        ])    
        return fig
    def addPoint(self,fig,xv,yv,caption,colorPoint='blue',size=10):
        fig.add_trace(go.Scatter(x=xv,y=yv,mode='markers',marker={'color':colorPoint,'size':size}
                                )
        )
        return fig

    def addLine(self,fig,xv,yv,caption,mode,colorLine='',colormarker='',dash='solid',size=10):
        # lines or lines_markers or markers
        if len(xv)>0:
             if not 'markers' in mode:
                if colorLine=='':
                    scat=go.Scatter(x=xv, y=yv, name=caption,
                                mode=mode,hovertemplate=None,line={'width':2,'dash':dash} )
                else:
                    scat=go.Scatter(x=xv, y=yv, name=caption,
                                mode=mode,hovertemplate=None,line={'width':2,'dash':dash,'color':colorLine} )
             if 'markers' in mode:
                scat=go.Scatter(x=xv, y=yv, name=caption,
                                mode=mode,hovertemplate=None,marker={'size': size,'color':colormarker} )
             fig.add_trace(scat)

        return fig

    def closePlot(self,fig,idG,tit,wid,hei='',tmax='',vmin='',vmax='',mode=''):
        #fig.update_xaxes(tickformat="%d/%m")
        #ticklabelmode="period")
        if mode=='print' or mode=='HTML':
            fontSize=int(wid/800*10)*4
            if fontSize<5:fontSize=5
        else:
            fontSize=14
        fig.update_xaxes(tickfont={'size':fontSize})
        fig.update_yaxes(tickfont={'size':fontSize})

        fig.update_layout(hovermode="x unified")
        if tmax !='':
            fig.update_xaxes(range=[0, tmax])
        if vmax !='':
            fig.update_yaxes(range=[vmin, vmax])  
        fig.update_layout(width=wid, height=hei)
        fig.update_layout(title={'text': tit,'xanchor': 'center','yanchor': 'top','font':{'size':fontSize}},title_x=0.5)
        fig.update_layout (paper_bgcolor="white",plot_bgcolor='#F5F6CE')
        fig.update_traces(line=dict(width=3))
        if mode=='print' or mode=='HTML':
            #fig.update_layout(legend={'itemsizing': 'constant','orientation':'h','yanchor':'bottom','y':-1,
            #                          'font':{'size':fontSize}})
            fig.update_layout(showlegend=False)
            fig.update_layout(plot_bgcolor='white', 
                              margin=dict(l=20, r=20, t=20, b=20)) #, paper_bgcolor="LightSteelBlue",)
            fig.add_shape(
        # Rectangle with reference to the plot
            type="rect",
            xref="paper",
            yref="paper",
            x0=0,
            y0=0,
            x1=1.0,
            y1=1.0,
            line=dict(
                color="black",
                 width=1,
             )
            )
            fig.update_layout()
            grafico=dcc.Graph(id=idG,figure=fig,config={'displayModeBar': False})
        else:
            grafico=dcc.Graph(id=idG,figure=fig)
        return grafico,fig
    def fnullNumeric(self,a):
        #print('a=',a)
        if a==None or a=='':
            return 0.0
        else:
            if type(a)==str:
                a=float(a)
        return a
    def creaPlots(self,codicePaz,codiceVis='',wid=800,hei=400,mode=''):
        db=dbase(dbname)
        pa=db.getTableRecord('Pazienti','Codicepaziente='+format(codicePaz))[0]
        vi=db.getTableRecord('Visite','Paziente='+format(codicePaz))        
        perc=db.getTableRecord('Percentili')
        db.close()
        dnS=pa['DatadiNascita']
        dn=parseDate(dnS)
        Nome=pa['Nome']
        Cognome=pa['Cognome']
        Sesso=pa['Sesso']
        sizePoints=10
        if mode=='print' or mode=='HTML':
            sizePoints=5
        if Sesso=='M':
            ses='Maschi'
        else:
            ses='Femmine'
        dati={'Peso':{'x':[],'y':[]},'Statura':{'x':[],'y':[]},'CircCran':{'x':[],'y':[]},}
        currvi={}
        for k in range(len(vi)):
            vis=vi[k]
            codV=vis['CodiceVisita']
            dvS=vis['DataVisita']
            dv=parseDate(dvS)
            etamesi=CalcolaEta(dn,dv,True)
            peso=self.fnullNumeric(vis['PesoRilevato(gr)'])/1000
            #print(dn,dv,etamesi,peso)
            lung=self.fnullNumeric(vis['Lunghezza(cm)'])
            circ=self.fnullNumeric(vis['CirconferenzaCranica'])
            if format(codV)==format(codiceVis) and codiceVis !='':
                currvi['etamesi']=etamesi
                currvi['Peso']=peso
                currvi['Statura']=lung
                currvi['CircCran']=circ
            if not (peso==0):
                dati['Peso']['x'].append(etamesi)
                dati['Peso']['y'].append(peso)
            if not (lung==0):
                dati['Statura']['x'].append(etamesi)
                dati['Statura']['y'].append(lung)
            if not (circ==0):
                dati['CircCran']['x'].append(etamesi)
                dati['CircCran']['y'].append(circ)
        figs=[]
        for tipo in ['Peso','Statura','CircCran']:
            fig=self.creaPlot(tipo)        
            xp={'3%':[],'50%':[], '97%':[]};pv={'3%':[],'50%':[], '97%':[]}
            for p in perc:                
                for valP in ['3%','50%','97%']:
                  if p[tipo+ses+valP]!=-1:
                    xp[valP].append(p['Eta'])
                    pv[valP].append(p[tipo+ses+valP])
            for valP in ['3%','50%','97%']:            
                #print(xp[valP],pv[valP])
                if valP=='50%':
                    dash='solid'
                else:
                    dash='dash'
                fig=self.addLine(fig,xp[valP],pv[valP],valP,'lines','red','',dash)
                    
            if len(dati[tipo]['x'])>0:
                tmax=dati[tipo]['x'][-1]*1.1
                vmax  =pv['97%'][-1]
                vmin  =pv['3%'][0]
                for j in range(len(xp['97%'])):
                    if xp['97%'][j]>tmax:
                        vmax=pv['97%'][j]
                        break
                
            else:
                tmax='';vmax='';vmin=''
            print('sz:',sizePoints)
            fig=self.addLine(fig,dati[tipo]['x'],dati[tipo]['y'],Nome+' '+Cognome,'markers','','navy',sizePoints)
            if currvi !={} :
                if tipo in currvi:
                    if currvi[tipo]>0:
                        fig=self.addLine(fig,[currvi['etamesi']],[currvi[tipo]],'Questa visita','markers','','red','',sizePoints*2)
            graf,fig=self.closePlot(fig,tipo,tipo+' percentile',wid,hei,tmax,vmin,vmax,mode)
            if mode=='HTML':
                figs.append(fig)
            else:
                figs.append(graf)
        return figs


