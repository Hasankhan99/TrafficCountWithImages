import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def ErrorLog(detail, date, dbfile):
    conn = create_connection(dbfile)
    try:
        conn.execute('CREATE TABLE IF NOT EXISTS ErrorLog(ID INTEGER PRIMARY KEY AUTOINCREMENT, detail TEXT,date TEXT)')
        print('==============================', str(date))
        print("Table created successfully")
        conn.execute("INSERT INTO ErrorLog (storeuid, date) VALUES ("+str(detail)+",'"+str(date)+"')")
        conn.commit()
        conn.close()
    except Exception as ex:
        print('==============================: ',ex)

def CheckPreData(suid, date, dbfile):
    conn = create_connection(dbfile)
    try:
        conn.execute('CREATE TABLE IF NOT EXISTS CheckPreData(ID INTEGER PRIMARY KEY AUTOINCREMENT, storeuid TEXT,date TEXT)')
        print('==============================', str(date))
        print("Table created successfully")
        conn.execute("INSERT INTO CheckPreData (storeuid, date) VALUES ("+str(suid)+",'"+str(date)+"')")
        conn.commit()
        conn.close()
    except Exception as ex:
        print('==============================: ',ex)


def selectAllStores(conn, date, serverName):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """

    def dict_factory(cursor, row):
        d = dict()
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    # sqliteConnection = sqlite3.connect(conn)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    sql_select_query = "select camsdata.* from camsdata where camsdata.store_unique_id not in (select CheckPreData.storeuid from CheckPreData WHERE CheckPreData.date='"+str(date)+"') and status=1 and server_name='"+str(serverName)+"'"
    cursor = cur.execute(sql_select_query)
    record = cursor.fetchall()

    return record


def getMainSetting(conn, serverid):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """

    def dict_factory(cursor, row):
        d = dict()
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    # sqliteConnection = sqlite3.connect(conn)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    sql_select_query = "SELECT * FROM mainsetting where id="+str(serverid)+""
    cursor = cur.execute(sql_select_query)
    record = cursor.fetchone()
    return record


def main():
    database = r"/home/live/Documents/api_programst/db.sqlite3"

    # create a database connection
    conn = create_connection(database)
    with conn:
        print("2. Query all tasks")
        stores = selectAllStores(conn, '2021-07-11', 'Aiprod1')
        # print(getMainSetting(conn, 1))
        for i, str in enumerate(stores):
            if i>36:
                print(str)
        import datetime
        import time
        if(time.strftime("%m-%d-%Y")==time.strftime("%m-%d-%Y")):
            print("true")
        else:
            print("No Change")

if __name__ == '__main__':
    main()