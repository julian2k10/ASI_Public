import os
import time
import datetime
import asi_email
import pandas as pd
import requests
import logging
import mysql.connector as connector

root_dir = f"{os.getcwd()}"

retry_count = 0
error_message = 'None'
time_now = time.time()
asctime = str(datetime.datetime.fromtimestamp(time_now).strftime('%Y-%m-%d'))
sector_url = 'https://www.alphavantage.co/query?function=SECTOR&apikey=demo'
file_name = f"{root_dir}/Sector Performance.csv"
#Setup logging to file
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s %(name)-10s %(levelname)-8s %(message)s',
                   datefmt='%Y-%m-%d %H:%M',
                   filename=f'{root_dir}/Sector Perfromance log.log',
                   filemode='a')

#Define a handler to write INFO messages or higher to system output
console = logging.StreamHandler()
console.setLevel(logging.INFO)

#Setup output format for console.
formatter = logging.Formatter('%(name)-27s : %(levelname)-8s %(message)s')
console.setFormatter(formatter)

# add the handler to the root logger
logging.getLogger('').addHandler(console)

#setup loggers to debug program
logger = logging.getLogger('Update Sector Performance')
logger.info('Update Sectors Performance Active...\n')

def write_to_File(File_Name, data):
    with open(File_Name, 'w+') as f:
        status = f.write(str(data))
        
    return status

def read_from_File(File_Name):
    import ast
    data = 0
    try:
        with open(File_Name, 'r') as f:
            data = f.read()
            data = ast.literal_eval(data)
    except Exception:
        return data

    return data

connection = read_from_File(f'{root_dir}/DB_connection.txt')

def get_sector_performance(url):
    keys = 'None'
    alphavantage = 'None'
    try:
        alphavantage = requests.get(url).json()
        keys = list(alphavantage.keys())
        
        if 'Meta Data' in keys:
            return alphavantage
        else:
            if len(keys) > 0:
                alphavantage = str(alphavantage[keys[0]])
            raise Exception(alphavantage)

    except Exception as ex:
        try:
            logger.error(ex.message)
            error_message = ex.message
        except:
            logger.error(ex)
            error_message = ex

        time.sleep(1800)

        retry_count = 1
        while retry_count < 3:
            if 'Invalid API call' in alphavantage:
                return -1
            else:
                logger.error('Server Error! will retry in 60 sec...')
                time.sleep(60)
                alphavantage = requests.get(url).json()
                keys = list(alphavantage.keys())
                retry_count +=1
        
                if 'Meta Data' in keys:
                    return alphavantage
            return 0

def table_to_csv(file_name, table):
    """
    file_name : string - name of csv file
    table : DataFrame or list of panda DataFrames objects
    """
    with open(file_name, 'a') as f:
        size = len(table)
        try:
            if isinstance(table, list):
                for x in range(size):
                    table[x].to_csv(f, header=True, sep=',', line_terminator='\n')
            
            elif isinstance(table, pd.DataFrame):
                table.to_csv(f, header=True, sep=',', line_terminator='\n')

        except Exception as ex:
            try:
                logger.error(ex.message)
                error_message = ex.message
            except:
                logger.error(ex)
                error_message = ex

            time.sleep(1800)

def table_to_sql(table, db_connection):
    """
    table : DataFrame or list of panda DataFrames objects

    db_connection : 1. Semicolon seperated connection string:
                    e.g "host=143.43.231.3;user=root;passwd=myDBpass123!!;database=system_db"}
                    
                    2. Dictionary object with connection info :
                    e.g {'host':'143.43.231.3', 'user':'root', 'passwd':'myDBpass123!!', 'database':'system_db'}
    """
    host =''
    user =''
    passwd =''
    database =''
    row_count = 0
    logger.info('Updating SQL database...')
    try:
        if isinstance(db_connection, str):
            db_connect = db_connection.split(';')
            for info in db_connect:
                info = info.split('=')
                if 'host' in info:
                    host = info[1]
                if 'user' in info:
                    user = info[1]
                if 'passwd' in info:
                    passwd = info[1]
                if 'database' in info:
                    database = info[1]

        if isinstance(db_connection, dict):
            host = db_connection['host']
            user = db_connection['user']
            passwd = db_connection['passwd']
            database = db_connection['database']

        mydb = connector.connect(host=host,
                                 user=user,
                                 passwd=passwd,
                                 database=database
                                 )

        db_cursor = mydb.cursor()

        sql = "INSERT INTO sectors_performance (date, rank, sector, performance) VALUES (%s, %s, %s, %s)"

        if isinstance(table, pd.DataFrame):
            size = len(table.index)
            for x in range(size):
                record = table.iloc[x]
                _date = str(record.Date)
                _rank = str(record.Rank)
                _sector = str(record.Sector)
                _performance = str(record.Performance)

                _date = datetime.datetime.strptime(_date, '%m/%d/%Y')
                _date = _date.strftime('%Y-%m-%d')

                values = (_date, _rank, _sector, _performance)
                db_cursor.execute(sql, values)
                mydb.commit()
                row_count += db_cursor.rowcount

            logger.info(f"{row_count} record inserted.")

        if isinstance(table, list):
            for _table in table:
                size = len(_table.index)
                for x in range(size):
                    record = _table.iloc[x]
                    _date = str(record.Date)
                    _rank = str(record.Rank)
                    _sector = str(record.Sector)
                    _performance = str(record.Performance)

                    _date = datetime.datetime.strptime(_date, '%m/%d/%Y')
                    _date = _date.strftime('%Y-%m-%d')

                    values = (_date, _rank, _sector, _performance)
                    db_cursor.execute(sql, values)
                    mydb.commit()
                    row_count += db_cursor.rowcount

            logger.info(f"{row_count} record inserted.")

    except Exception as ex:
        try:
            logger.error(ex.message)
            error_message = ex.message
        except:
            logger.error(ex)
            error_message = ex

        time.sleep(1800)
    
    finally:
            return row_count

def refresh_db_index(db_connection):
    """
    table : DataFrame or list of panda DataFrames objects

    db_connection : 1. Semicolon seperated connection string:
                    e.g "host=143.43.231.3;user=root;passwd=myDBpass123!!;database=system_db"}
                    
                    2. Dictionary object with connection info :
                    e.g {'host':'143.43.231.3', 'user':'root', 'passwd':'myDBpass123!!', 'database':'system_db'}
    """
    host =''
    user =''
    passwd =''
    database =''
    logger.info('Reindexing SQL database...')
    try:
        if isinstance(db_connection, str):
            db_connect = db_connection.split(';')
            for info in db_connect:
                info = info.split('=')
                if 'host' in info:
                    host = info[1]
                if 'user' in info:
                    user = info[1]
                if 'passwd' in info:
                    passwd = info[1]
                if 'database' in info:
                    database = info[1]

        if isinstance(db_connection, dict):
            host = db_connection['host']
            user = db_connection['user']
            passwd = db_connection['passwd']
            database = db_connection['database']

        mydb = connector.connect(host=host,
                                 user=user,
                                 passwd=passwd,
                                 database=database
                                 )

        db_cursor = mydb.cursor()
        db_cursor.execute("SELECT * FROM sectors_performance")
        result = db_cursor.fetchall()

        idx = 1
        for record in result:
            row_index = record[0]
            sql = "UPDATE `asi_db`.`sectors_performance` SET `sectors_performance_id` = '%s' WHERE (`sectors_performance_id` = '%s');"
            db_cursor.execute(sql, (idx, row_index))
            idx += 1

        mydb.commit()

    except Exception as ex:
        try:
            logger.error(ex.message)
            error_message = ex.message
        except:
            logger.error(ex)
            error_message = ex

        time.sleep(1800)

def json_to_table(data):
        try:
            if isinstance(data, dict):
                _table = 'None'
                logger.info('Creating table...')
                column_names = ['Date', 'Rank', 'Sector', 'Performance']
                df = 'None'
                table = list()
                sector = list()
                performance = list()
                table_names = list(data.keys())
                refresh_date = 'None'
                for x in range(len(table_names)):
                    table_name = table_names[x].split(':')
                    fields = data[table_names[x]]
                    column = list(fields.keys())
                    rows = list(fields.values())
                    #Strip percentage sign from data
                    for y in range(len(rows)):
                        rows[y] = rows[y].strip('%')

                    if 'Meta Data' in table_name:
                        refresh_date = rows[1][-10:]
                    else:
                        table_name = table_name[1].strip(' \t\n')
                        sectors = list(column)
                        performance = list(rows)
                        column.insert(0, table_name)
                        rows.insert(0, table_name)
                        column.insert(0, refresh_date)
                        rows.insert(0, refresh_date)
                        date = list()
                        rank = list()
                        for x in range(len(sectors)):
                            date.append(column[0])
                            rank.append(column[1])

                        table.append(pd.DataFrame({'Date':date, 'Rank':rank, 'Sector':sectors, 'Performance':performance}))

                _table = table
            else:
                logger.info('Invalid Datatype! JSON object expected!')
                    
        except Exception as ex:
            try:
                logger.error(ex.message)
                error_message = ex.message
            except:
                logger.error(ex)
                error_message = ex

            time.sleep(1800)
        finally:
            return _table

#Get date of latest update
latest_sector_date = read_from_File(f'{root_dir}/latest_sector_date.txt')
latest_sector_date = str(latest_sector_date)
last_checked = latest_sector_date

while True:
    try:
        current_time = time.time()
        localtime = time.localtime(time.time())
        today = str(datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d'))

        if localtime.tm_hour >= 10 and last_checked != today:
            logger.info('Getting sector performance...')
            data = get_sector_performance(sector_url)
            if not isinstance(data, int):
                current_date = data['Meta Data']['Last Refreshed'][-10:]
                current_date = datetime.datetime.strptime(current_date, '%m/%d/%Y')
                current_date = str(current_date.strftime('%Y-%m-%d'))

                if latest_sector_date != current_date:
                    table = json_to_table(data)
                    results = table_to_sql(table=table, db_connection=connection)
                    if results > 0:
                        retry_count = 0 
                        latest_sector_date = current_date  
                        logger.info('<<Sector Performance Updated!>>') 
                        write_to_File(File_Name='latest_sector_date.txt', data=latest_sector_date)                       
                        time.sleep(1800) 
                    else:
                        retry_count += 1
                        time.sleep(10)
                        if retry_count >= 5:
                            html = asi_email.create_simple_html_message(title='Error Updating Sector Performance!', text=error_message)
                            logger.info('html message created! sending emails...')
                            asi_email.send_html_message("Error Updating Sector Performance!", html)
                            break
                else:
                    last_checked = today 
                    time.sleep(1800)
            else:
                logger.error('Error getting data from server!')
        else:
            time.sleep(900)

    except Exception as ex:
        try:
            logger.error(ex.message)
            error_message = ex.message
        except:
            logger.error(ex)
            error_message = ex

        time.sleep(1800)