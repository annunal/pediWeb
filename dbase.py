import sqlite3
import datetime
import os


class dbase(object):
    """description of class"""

    def __init__(self,dbname):        
        #print('Opening database ',dbname)
        init=False
        if not os.path.exists(dbname):
            print('database not existing')
        else:
            self.con=sqlite3.connect(dbname)
            self.cursorObj=self.con.cursor()
        
    def close(self):
        self.cursorObj.close()
        self.con.close()

    def getRecord(self,sql):
        #print(sql)
        self.cursorObj.execute(sql)
        rows = self.cursorObj.fetchall()
       # for row in rows:
        #    print(row)
        return rows
    def execSQL(self,sql):
        try:
            #print(' sto per eseguire')
            self.cursorObj.execute(sql)
            #print('-1-')

            ret= self.con.commit()
            #print('-2-')
            return ret
        except Exception as e:
            print(e,sql)
            return False
        

    def getTableRecord(self,tab,where=''):
        try:
            fields=self.getRecord("PRAGMA table_info('"+tab+"')")
            sql='SELECT * from '+tab
            if where !='':
                sql+=' WHERE '+where
            #print(sql)
            rows=self.getRecord(sql)
            tab=[]
            for row in rows:
                rec={}
                for n in range(len(row)):
                    rec[fields[n][1]]=row[n]
                tab.append(rec)
        except Exception as e:
            print(sql,e)
        return tab

    def getFields(self,tab):
        fields=self.getRecord("PRAGMA table_info('"+tab+"')")
        n=-1
        ov={}
        for f in fields:            
            n +=1
            fname=f[1]
            ov[fname]=n
        #print(ov)
        return ov
