import sqlite3
from sqlite3 import Error
from .models import ClicksInfo

class LoadDB:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def create_connection(self):
        """ create a database connection to the SQLite database
            specified by the self.db_path path
        :return: Connection object or None
        """
        
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
        except Error as e:
            print(e)
     
        return conn
 

    def get_all_rows(self, conn):
        # creation status success log
        stat_log = {}
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM clicksinfo")
        
        rows = cur.fetchall()
        
        row_counter = 0
        for row in rows:
            
            object, created = ClicksInfo.objects.get_or_create(
                                                          date=row[0],
                                                          channel=row[1],
                                                          country=row[2],
                                                          os=row[3],
                                                          impressions=row[4],
                                                          clicks=row[5],
                                                          installs=row[6],
                                                          spend=row[7],
                                                          revenue=row[8],
                                                          )
            
            print('Row {} Status {}'.format(row_counter, created))
            stat_log[row_counter] = created
            
            row_counter += 1
        
        return stat_log
        
    def load_db(self):
        # create a database connection
        conn = self.create_connection()
        with conn:
            print("Get all rows from DB")
            status = self.get_all_rows(conn)
            
        # print success status log for each of all the tables in the db
        print(status)
        # print final success status of ALL tables (single True or False)
        print('Final Status {}'.format(all(value == True for value in status.values())))

'''            
dbloader = DBLoader('sample_db.sqlite3')
dbloader.load_db()'''