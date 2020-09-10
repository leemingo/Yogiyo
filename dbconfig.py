import pymysql

siteName = 'YOGIYO'

class MysqlController:
    def __init__(self, host, port, id, pw, db_name):
        self.conn = pymysql.connect(host=host, port=port, user=id, password=pw, db=db_name, charset='utf8')
        self.curs = self.conn.cursor()

    def insert_key(self, keydata):
        sql = "INSERT INTO Crawl_Key VALUES (%s, '" + keydata + "', '')"
        self.curs.execute(sql, (siteName, str(keydata), ))
        self.conn.commit()

    def search_key(self, keydata):
        sql = "SELECT COUNT(*) AS Count FROM Crawl_Key WHERE SiteName=%s AND KeyData = %s"
        rows = self.curs.execute(sql, (siteName, str(keydata), ))
        return rows

    def searchinsert_key(self, keydata):
        #사용안함.
        sql = "SELECT COUNT(*) AS Count FROM Crawl_Key WHERE SiteName=%s AND KeyData = %s"
        self.curs.execute(sql, (siteName, str(keydata), ))
        rows = self.curs.fetchone()

        if rows[0] == 0:
            sql = "INSERT INTO Crawl_Key VALUES (%s, %s, '')"
            self.curs.execute(sql, (siteName, str(keydata), ))
            self.conn.commit()

    def searchinsert_key2(self, keydata, saddr):
        sql = "SELECT COUNT(*) AS Count FROM Crawl_Key WHERE SiteName=%s AND KeyData = %s"
        self.curs.execute(sql, (siteName, str(keydata), ))
        rows = self.curs.fetchone()

        if rows[0] == 0:
            sql = "INSERT INTO Crawl_Key(SiteName, KeyData, isCheck, isAddr) VALUES (%s, %s, '', %s)"
            self.curs.execute(sql, (siteName, str(keydata), saddr,))
            self.conn.commit()

    def selectisaddr(self, sisdata):
        sql = "SELECT * FROM Crawl_Key WHERE SiteName=%s AND IsAddr=%s"
        rows = self.curs.execute(sql, (siteName, str(sisdata), ))
        return self.curs.fetchall()

    def selectisaddr2(self, sisdata):
        sql = "SELECT SiteName, KeyData, isCheck, isAddr, isDate FROM Crawl_Key WHERE SiteName=%s AND IsAddr like %s and isDate =''"
        rows = self.curs.execute(sql, (siteName, str(sisdata)))
        return self.curs.fetchall()

    def selectisaddr_se(self, sisdata, startnum, endnum, reviews, reviewe):
        sql = "SELECT SiteName, KeyData, isCheck, isAddr, isDate FROM Crawl_Key WHERE SiteName=%s AND IsAddr like %s and KeyData >= %s and KeyData < %s and KeyData <> '' and isDate ='' and isCheck='' and isReviewCnt >= %s and isReviewCnt < %s "
        rows = self.curs.execute(sql, (siteName, str(sisdata),startnum, endnum, reviews, reviewe))
        return self.curs.fetchall()

    def selectisaddr_isdatespace(self):
        sql = "SELECT SiteName, KeyData, isCheck, isAddr, isDate FROM Crawl_Key WHERE SiteName=%s AND isDate =''"
        rows = self.curs.execute(sql, (siteName))
        return self.curs.fetchall()

    def update_isCheck(self, sdatetime, keydata):
#        sql = "UPDATE Crawl_Key SET isCheck='1', isDate=%s WHERE SiteName=%s AND KeyData=%s"
        sql = "UPDATE Crawl_Key SET isDate=%s WHERE SiteName=%s AND KeyData=%s"
        self.curs.execute(sql, (sdatetime, siteName, str(keydata)))
        self.conn.commit()


    def update_isCheckData(self, sdatetime, keydata):
        sql = "UPDATE Crawl_Key SET isCheck=%s  WHERE SiteName=%s AND KeyData=%s"
        self.curs.execute(sql, (sdatetime, siteName, str(keydata)))
        self.conn.commit()


    def insertDeatil(self, keydata, sData1, sData2):
#        sql = "SELECT COUNT(*) AS Count FROM Crawl_BlueRS WHERE SiteName=%s AND Store_Num=%s"
        sql = "SELECT COUNT(*) AS Count FROM Crawl_BlueRS WHERE Store_Num=%s"
        self.curs.execute(sql, (str(keydata) ))
        rows = self.curs.fetchone()

        if rows[0] == 0:
            sql = "INSERT INTO Crawl_BlueRS(Store_Name, Store_Num, JSonData) VALUES(%s, %s, %s)"
            self.curs.execute(sql, (str(sData1), str(keydata), sData2))
            self.conn.commit()

    def insertDeatil_Y(self, keydata, sData1, sData2, sData3, sData4, sData5):
#        sql = "SELECT COUNT(*) AS Count FROM Crawl_YOGIYO WHERE SiteName=%s AND Store_Num=%s"
        sql = "SELECT COUNT(*) AS Count FROM Crawl_YOGIYO WHERE Store_Num=%s"
        self.curs.execute(sql, (str(keydata) ))
        rows = self.curs.fetchone()

        if rows[0] == 0:
            sql = "INSERT INTO Crawl_YOGIYO(Store_Name, Store_Num, Store_Info, Store_Menu, Store_Review, Store_Addr) VALUES(%s, %s, %s, %s, %s, %s)"
            self.curs.execute(sql, (sData1, str(keydata), sData2, sData3, sData4, sData5))
            self.conn.commit()

    def insertDeatil_MenuUpDate(self, keydata, sData1):
#        sql = "SELECT COUNT(*) AS Count FROM Crawl_YOGIYO WHERE SiteName=%s AND Store_Num=%s"
        sql = "SELECT COUNT(*) AS Count FROM Crawl_YOGIYO WHERE Store_Num=%s"
        self.curs.execute(sql, (str(keydata) ))
        rows = self.curs.fetchone()

        if rows[0] == 1:
            sql = "UPDATE Crawl_YOGIYO SET Store_Menu=%s WHERE Store_Num=%s"
            self.curs.execute(sql, (sData1, str(keydata)))
            self.conn.commit()


    def select_yogiyo_num(self, startnum, endnum):
        sql = "SELECT seq, Store_Name, Store_num FROM Crawl_YOGIYO WHERE Store_Num>=%s and Store_Num<%s"
        rows = self.curs.execute(sql, (startnum, endnum))
        return self.curs.fetchall()

#fetchall