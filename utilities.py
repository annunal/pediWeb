from datetime import datetime
from CONF import dbname, SAVEDIR
from cryptography.fernet import Fernet
import os,json
import socket,requests
from dbase import dbase
import dateparser
from ftplib import FTP

def  tds(w='',fontStyle='',fontSize='',bgcol='',fbol='',fontColor='',align='',borderColor=''):
    if w=='':
        tds={'padding':'2px',"overflow": "hidden",'no-wrap':True,'vertical-align':'top'}
    else:
        if type(w)==str:
            tds={'padding':'2px','width':w,"overflow": "hidden",'no-wrap':True,'vertical-align':'top'}
        else:
            tds={'padding':'2px','width':format(w)+'px',"overflow": "hidden",'no-wrap':True,'vertical-align':'top'}
    if bgcol !='':
        tds['backgroundColor']=bgcol
    if borderColor !='':
        tds['border-color']=borderColor
        tds['border']='1px solid'
    if fontStyle !='':
        tds['font-style']=fontStyle
    if fontSize!='':
       tds['font-size']=format(fontSize)+'px'
    if fbol!='':
       tds['font-weight']=fbol
    if fontColor!='':
       tds['color']=format(fontColor)
    if align !='':
        tds['text-align']=align
    return tds

def ValutaPerc(quantita, tipo, txtSesso, etamesi):
        if quantita=='':
            return ''
        #Static mi, peso3, peso97, peso50, peso0, x(10), peso(10), i, etamesi, perc
        x=[0]*10
        peso=[0]*10
        dpeso50=[0]*2
        dpeso3=[0]*2
        dpeso97=[0]*2
        p = float(quantita)

        if tipo == "Peso":
            if p < 1000: p = p * 1000
            peso0 = p / 1000
        else:
            peso0 = float(p)
        
        if etamesi <= 24:
            mi1 = int(etamesi / 3 + 0.0001) * 3
            mi2 = mi1 + 3
        else:
            mi1 = int(etamesi / 12) * 12
            mi2 = mi1 + 12


        db=dbase(dbname)
        rs = db.getTableRecord('Percentili',"Eta>=" +format( mi1) + " and Eta<=" + format(mi2))
        #print("Eta>=" +format( mi1) + " and Eta<=" + format(mi2))
        db.close()
        sesso = "Maschi" ; 
        if txtSesso == "F": 
            sesso = "Femmine"
        qua = tipo
        if not rs==[]:
            if len( rs) > 1:
                    if rs[0][qua +sesso + "3%"]!=-1 and rs[1][qua +sesso + "3%"]!=-1:

                        for j in range(2):
                           # print(rs[j][qua + sesso + "3%"],rs[j][qua + sesso + "50%"],rs[j][qua + sesso + "97%"])
                            dpeso3[j]  = float(rs[j][qua + sesso + "3%"])
                            dpeso50[j] = float(rs[j][qua + sesso + "50%"])
                            dpeso97[j] = float(rs[j][qua + sesso + "97%"])

                    else:
                        return "n.a."
                        
            else:                
                return "n.a."
        else:
            return "n.a"

        peso50 = dpeso50[0] + (dpeso50[1] - dpeso50[0]) / (mi2 - mi1) * (etamesi - mi1)
        peso97 = dpeso97[0] + (dpeso97[1] - dpeso97[0]) / (mi2 - mi1) * (etamesi - mi1)
        peso3 = dpeso3[0] + (dpeso3[1] - dpeso3[0]) / (mi2 - mi1) * (etamesi - mi1)

        x[1] = 3 ;  peso[1] = peso3
        x[2] = 10 ; peso[2] = peso3 + (peso50 - peso3) * 0.55 / 1.9
        x[3] = 25 ; peso[3] = peso3 + (peso50 - peso3) * 1.25 / 1.9
        x[4] = 50 ; peso[4] = peso50
        x[5] = 75 ; peso[5] = (peso97 - peso50) * 0.6 / 2.1 + peso50
        x[6] = 90 ; peso[6] = (peso97 - peso50) * 1.4 / 2.1 + peso50
        x[7] = 97 ; peso[7] = peso97
        perc = 98
        for i in range(1,8):
            if peso0 < peso[i]:
                if i == 1:
                    perc = 2
                else:
                    perc = x[i - 1] + (x[i] - x[i - 1]) / (peso[i] - peso[i - 1]) * (peso0 - peso[i - 1])
                    break
                            

        if perc > 97:
            return "97"
        elif perc < 3:
            return "3"
        else:
            return format(int(perc))        





def CalcolaEta(dn,dv,etamesi=False):      
      days = (dv-dn).total_seconds()/3600/24
      y = int(days / 365.25)
      m = int((days - y * 365.25) / 30)
      g = int(days - y * 365.25 - m * 30)
      m0 = y * 12 + m + g / 30
      mesi = m0
      if etamesi:
          return mesi
      if m0 < 12:
            Eta = format(m) + " m "
            if g > 0: Eta +=  "- " + format(g) + " g"
      elif m0 >= 12 and m0 < 24:
            Eta = format(y * 12 + m) + " m "
      elif m0 >= 24:
            Eta = format(y) + "a "
            if m > 0: Eta +=  "- " + format(m) + " m"
      
      return Eta.strip()

def EncUsPw(uname,pwd,p3='',p4='',p5=''):
    f=Fernet(getkey())
    p1=format(uname) +"||" + format(pwd)
    if p3!='':
        p1 +='||'+format(p3)
    if p4!='':
        p1 +='||'+format(p4)
    if p5!='':
        p1 +='||'+format(p5)
    enc=f.encrypt(p1.encode()).decode()
    return enc
def DecUsPw(d):
    f=Fernet(getkey())
    try:
        p1=f.decrypt(d.encode()).decode()
    except Exception as e:
        print('error: ',e)
        p1='||'
    #user=p1.split('||')[0]
    #pwd=p1.split('||')[1]
    return p1.split('||')
    #return user,pwd

def getkey():
    if not os.path.exists(SAVEDIR+os.sep+'_basedata'):
           os.makedirs(SAVEDIR+os.sep+'_basedata')

    if os.path.exists(SAVEDIR+os.sep+'_basedata'+os.sep+'key.txt'):    
        file=open(SAVEDIR+os.sep+'_basedata'+os.sep+'key.txt','rb')
        key=file.read()
        file.close()
    else:
        key = Fernet.generate_key()
        file = open(SAVEDIR+os.sep+'_basedata'+os.sep+'key.txt', 'wb')  # Open the file as wb to write bytes
        file.write(key)  # The key is type bytes still
        file.close()
    return key

def checkUsPw(UPenc,pathname=''):
    if UPenc =='' and pathname=='':
        return False,'','','','','',''
    f=Fernet(getkey())
    
    if pathname !='':
        UPenc=pathname.split('/ID=')[1]
    try:
        p1=f.decrypt(UPenc.encode()).decode()
    except Exception as e:
        print('error: ',e)
        p1='||'
    user=p1.split('||')[0]
    pwd=p1.split('||')[1]
    db=dbase(dbname)
    userData=db.getTableRecord('users','userID="'+user+'" and password="'+pwd+'"')
    db.close()
    #print('userData=',userData,'users','userID=\''+user+'\' and password=\''+pwd+'\'')
    if userData==[]:
        return False,'','','','','',''
    userData=userData[0]
#    print(userData)
    if userData=={}:
        return False,'','','','','',''
    else:
        if userData['password']==pwd:
            name=userData['Nome']+' '+userData['Cognome']
            role=userData['Role']
            ID=userData['ID']
            emailID=userData['email']
            return True,user,pwd,name,role,ID,emailID
        else:
            return False,'','','','','',''

def sendMail(to,subject,testo,cc='alessandro.annunziato@gmail.com',bcc='',att=''):

    try:
        machine=socket.gethostname()

        URL='http://www.sportinlinea.it/sMail.asp'
        param="e_mail=$EMAIL&FromName=Bilance&FromAddress=casalverde@sportinlinea.it&subject=$SUBJECT&body=$BODY&cc=$CC&bcc=$BCC&attachment=$ATT"

        while "<br>" in testo:
            testo=testo.replace("<br>","$BR$")
        while "<br />" in testo:
            testo=testo.replace("<br />","$BR$")
        while "<br/>" in testo:
            testo=testo.replace("<br/>","$BR$")
        while "<//br>" in testo:
            testo=testo.replace("<//br>","$BR$")
        while "<" in testo:
            testo=testo.replace("<","$LT$")
        while ">" in testo:
            testo=testo.replace(">","$GT$")
        while "&" in testo:
            testo=testo.replace("&","$AND;")
        while "?" in testo:
            testo=testo.replace("?","$QUEST;")
        while "\n" in testo:
            testo=testo.replace("\n","$BR$")
        #if machine !='localhost' and machine !='ECMLAA-NB01' or True:
        #    now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #    f=open(mailFile,'a')
        #    f.write('$STARTMAIL$'+'$|$'.join([now,to,subject,testo,cc,bcc,'TO SEND',''])+'$ENDMAIL$\n')
        #    f.close
        #    return ''

        param=param.replace("$EMAIL",to)
        param=param.replace("$SUBJECT",subject)
        param=param.replace("$BODY",testo)
        param=param.replace("$CC",cc)
        param=param.replace("$BCC",bcc)
        param=param.replace("$ATT",att)

        url=URL +"?" + param

        print(url)
        r = requests.get(url, allow_redirects=True)
        #print(r.status_code)
        #print(r.content)
        return 'code: '+format(r.status_code)+' status: '+format(r.content)
    except Exception as e:
        print(e)
        return e

def sendMail0(to,subject,body,cc='',bcc=''):
        import smtplib
        try:
            machine=socket.gethostname()
            if machine !='localhost' and machine !='ECMLAA-NB01':
                return 
            mode=2

        #        return sendEmailMessage('test',to,subject,body)
        #        return False
        # gmail
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            pwdemail='RomaTaino2021'
            uname='alessandro.annunziato@gmail.com'

            server=smtplib.SMTP_SSL('out.postassl.it',465)
            uname='casalverde@sportinlinea.it'
            pwdemail='RomaTaino2021'
        #mailjet
        #        server=smtplib.SMTP_SSL('in-v3.mailjet.com',465)
        #        pwdemail='4eb1d36d07819af5425a53ee833a5121'
        #        uname='51d249b4d48c4bb312533b99e137b7c8'
        #pulse
        #        #uname='alessandro.annunziato@gmail.com'
        #        #pwdemail='PiNS3gqtpr'
        #        #server=smtplib.SMTP_SSL('smtp-pulse.com',465)
            server.login(uname,pwdemail)
            if mode==1:
            
                resp=server.sendmail('alessandro.annunziato@gmail.com',to,'Subject: '+subject+'\n\n'+body)                                                          
                resp=server.sendmail('alessandro.annunziato@gmail.com',cc,'Subject: '+subject+'\n\n'+body)
                server.quit()
            else:
                #from email.mime.multipart import MIMEMultipart
                from email.message import EmailMessage 
                me = "alessandro.annunziato@gmail.com"

                rcpt = [to]
                if bcc !='': rcpt += bcc.split(",") 
                if cc !='': rcpt += cc.split(",") 

                msg = EmailMessage() #MIMEMultipart('alternative')
                msg.set_content(body)
                msg['Subject'] = subject
                msg['From'] = me
                msg['To'] = to
                msg['Cc'] = cc
                msg['Bcc'] = bcc
            
        
                server.send_message(msg)
                server.quit()
        except Exception as e:
            print(e)
def getpath(nested_dict,id, values, prepath= (),result={}): 
    #print(len(nested_dict))
    #print(nested_dict.keys())
    if type(nested_dict)==str:
        return
    for k, v in nested_dict.items(): 
        #print(k)
        path = prepath + (k,) 
        if hasattr(v, 'items'):            
           if id in v.keys():
              if v[id] == values:
                # found value  
                  result[v[id]]=v                
                  return v 
# v is a dict 
           p = getpath(v, id, values, path, result) # recursive call 
           if p is not None: 
                return p
        elif type(v)==list:
            for elem in v:
               p = getpath(elem, id, values, path,result) # recursive call 
               if p is not None: 
                  return p

def fnull(a):
    if a==None:
        a=''
    return a
        
def getListaTipiVisite():
    db=dbase(dbname)
    tp=db.getTableRecord('tipiVisite')
    db.close()
    options=[]
    for rec in tp:
        if fnull(rec['Commento'])=='':
            elem={'label':rec['Tipodivisita'],'value':rec['CodiceVisita']}
        else:
            elem={'label':rec['Tipodivisita']+' ('+fnull(rec['Commento'])+')','value':format(rec['CodiceVisita'])}
        options.append(elem)
    optionsStr=json.dumps(options)
    #print(options)
    return tp,optionsStr

def parseDate(DatadiNascita): 
    if fnull(DatadiNascita)=='':
        return datetime.utcnow()
    try:
#        print('provo parser ',DatadiNascita)
        if (not '00:00:00' in DatadiNascita) and ('00:00' in DatadiNascita) and (not '/' in DatadiNascita):
            DatadiNascita+=':00'
        #print('in parser',DatadiNascita)
        dn=dateparser(DatadiNascita)
#        print('dn da dateparser',DatadiNascita,dn)
    except:
        if 'T' in DatadiNascita:
            try:
                dn=datetime.strptime(DatadiNascita,'%d/%m/%YT00:00')
            except:
                try:
                    dn=datetime.strptime(DatadiNascita,'%d/%m/%YT00:00:00')
                except:
                    dn=datetime.strptime(DatadiNascita,'%Y-%m-%dT00:00:00')
                    
        elif ' ' in DatadiNascita and '/' in DatadiNascita:
            dn=datetime.strptime(DatadiNascita,'%d/%m/%Y 00:00')
        elif ' ' in DatadiNascita and '-' in DatadiNascita:
            dn=datetime.strptime(DatadiNascita,'%Y-%m-%d 00:00:00')
        elif '-' in DatadiNascita:
            dn=datetime.strptime(DatadiNascita,'%Y-%m-%d')
        else:
            dn=datetime.strptime(DatadiNascita,'%d/%m/%Y')
        #printLog('data in parseDate',DatadiNascita)
        #printLog('data convertita',dn)

    return dn

def upload(host,user,pasw,localDir,remoteDir,fname):
    try:
        ftp=FTP(host)
        ftp.login(user,pasw)
        ftp.cwd(remoteDir)
        listfiles=ftp.nlst()
        if fname in listfiles:
            ftp.delete(fname)
        
        with open(localDir+os.sep+fname, 'rb') as file:
            ftp.storbinary(f'STOR {fname}', file)
        ftp.close()

        return True,'done'
    except Exception as e:
        return False,e