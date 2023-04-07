from schedaPaziente import creaTabVisita,getListaVisite

def createVisita_HTML(userID,codVisita,outFile,codPaz=''):
        print(userID,codVisita,codPaz,'role='+role+'<<<')
        tab,codPaz,email=creaTabVisita(userID,codVisita,'','','HTML')
        linkPrint=url+'/showVisita?enc='+idenc
        
        linkEmail='mailto:'+email+'?subject=[PEDIWEB] Scheda Visita&body=Visita Dott.ssa Bonini%0D%0A%0D%0ACliccare sul link o copiarlo e incollarlo in un browser:%0D%0A'+linkPrint
        
        grafs=''  #pl.creaPlots(codPaz,codVisita,180,170,modeHeader)
    
        dummy,options=getListaVisite(codPaz)
    
        currUser=html.Div(userID,id='currentUser')
        red=html.Div(id="hidden_div_for_redirect_callback")
        listaVisite,dummy=getListaVisite(codPaz,5,'HTML')
        layout='<HTML><BODY><CENTER>'+Navbar('HTML',userID)+'<TABLE><TR><TD>'+tab+'</TD><TD>'+grafs+'</TD></TABLE>'
        layout +='<B>Lista ultime 5 visite</B><BR>'+listaVisite
        layout +='</BODY></HTML>'

        with open(outFile,'w') as f:
            f.write(layout)
        return layout


