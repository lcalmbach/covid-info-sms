"""
covid_info_sms.py retrieves the last opendata.bs-covid record 
(https://data.bs.ch/explore/dataset/100073/table/?sort=timestamp) and checks 
the timestamp. If it is newer than the timestamp when the program was started, 
an sms text is generated with the key values and sent to a list of recipients. 

parameters:
frequency_secs: number of seconds between calls, default is 300
send initial:   true, if a message should be sent after starting the app. this is useful for testing, or 
                when running the app the first time, becasuse the record is new by definition. default is false


example:
python covid_alert.py 300, True
"""

from textmagic.rest import TextmagicRestClient
from datetime import datetime, timedelta
from urllib.request import urlopen
import pandas as pd
import json
import time
import sys
import config as cfg
import usr_pwd

__version__ = '0.1.3'
__author__ = 'Lukas Calmbach (lcalmbach@gmail.com)'

def get_status(current_record, last_record, SEND_INITIAL_MESSAGE) -> str:
    """
    returns the status of the current record as compared to the record retrieved 
    for the last fetch. if ht erecords are identical, there has been no change, if the timestamp 
    is newer, there was a new record, if the timestamps are identical but a field has ben updated, 
    the record was changed.   

    parameters: 
    last_record         previous record retrieved
    current_record      record retrieved now
    SEND_INITIAL_MESSAGE    force sending of record the first time

    returns:
    status              returns one of the following status:
        undefined:          one or both records are empty
        match:              both records are equal
        changed:            changes in the record but timestamp is identical
        new:                timestamp of current record is more recent than previous or SEND_INITIAL_MESSAGE
                            was set to True
    """


    
    result = 'new' if SEND_INITIAL_MESSAGE else 'undefined'

    if result == 'undefined' and last_record != {} and current_record != {}:
        # if there is no change at all > match
        if last_record == current_record:
            result = 'match' 
        else:
            last_rec_ts = datetime.strptime(last_record['timestamp'], "%Y-%m-%dT%H:%M:%S+00:00") 
            current_record_ts = datetime.strptime(current_record['timestamp'], "%Y-%m-%dT%H:%M:%S+00:00")
            # if timestamps are identical but there is a difference elsewhere
            if last_rec_ts == current_record_ts:
                 result = 'changed' 
            else:
                result = 'new' 
    return result
    

def get_recipients(status: str) -> str:
    """
    reads all recipients from a text file and returns a csv-string

    parameters:
    status: the status (new, changed, error) acts as a filter. each status is a column in the 
            recipients list. e.g. if status is changed only recipients with column changed set = 1 are returned

    returns:
    csv list of recipients in filter
    """

    recipients = ''
    try: 
        url = './recipients.txt'
        df_recipients = pd.read_csv(url, sep=';', engine='python', comment = '#', header=0, dtype=str)
        df_filtered = []
        if status == 'new':
            df_filtered = df_recipients.query('send_new == "1"')
        elif status == 'changed':
            df_filtered = df_recipients.query('send_update == "1"')
        else:
            df_filtered = df_recipients.query('send_error == "1"')
        lst = df_filtered['mobile'].tolist()
        recipients = ','.join(lst)
        print(recipients)
    except Exception as ex:
        print(f'An error occurred in function get_recipients(): {str(ex)}')
    finally:
        return recipients

def get_record(url:str)-> str:
    """
    retrieves the data using the REST url and transforms the data part into an object

    parameters:
    url         url to retrieve data

    returns:    record object
    """

    result = {}
    try: 
        jsonurl = urlopen(url)
        records = json.loads(jsonurl.read())
        if len(records) > 0:
            result = records['records'][0]['fields']
    except Exception as ex:
        print(f'An error occurred: {str(ex)}')
    return result


def send_message(recipients: str, text: str):
    """
    sends an sms to all entries in the recipients list.
    """

    try: 
        message = client.messages.create(phones=recipients, text=text)
        print(text)
    except Exception as ex:
        print(f'An error occurred: {str(ex)}')

def get_message(record: object, status: str) -> str:
    """
    returns the message string.
    """

    publish_timestamp = datetime.strptime(record['timestamp'], "%Y-%m-%dT%H:%M:%S+00:00")
    date_str = f"{datetime.strftime(publish_timestamp, '%d. %B')} {record['time']}"
    message = ''
    try: 
        if status == 'new':
            message = cfg.TEXT_TEMPLATE_NEW.format(date_str, 
                record['ndiff_conf'], 
                record['ndiff_deceased']) 
                #record['current_hosp']) die liegen erst am Nachmittag vor        
        else:    
            message = cfg.TEXT_TEMPLATE_CHANGED.format(date_str) 
            
    except Exception as ex:
        print(f'An error occurred: {str(ex)}')
    return message

def log_start(freq: int, init_flag: bool):
    """
    logs the start parameters to the terminal
    """

    print(f'Starting app: frequency(s) = {freq}, send initial sms: {init_flag}')

def log_status(record, last_update):
    """
    logs the current status to the terminal
    """

    try:    
        print(record['timestamp'], last_update, datetime.now())
    except Exception as ex:
        print(f'An error occurred in log_status: {str(ex)}')

if __name__ == "__main__":
    FREQUENCY_SECS = cfg.DEFAULT_FREQUENCY_SECS
    SEND_INITIAL_MESSAGE = cfg.DEFAULT_INITIAL_SEND_MSG_FLAG
    try:
        if int(sys.argv[1]) > 60:
            FREQUENCY_SECS = int(sys.argv[1])
        else: 
            raise Exception('frequency must be > 60s')
    except:
        print('frequency not valid')
    
    try:
        SEND_INITIAL_MESSAGE = (sys.argv[2]).lower() in ['true','1','y'] 
    except:
        print('sendinitialmessage not valid')
        
    last_record = get_record(cfg.COVID_URL)
    log_start(FREQUENCY_SECS, SEND_INITIAL_MESSAGE)
    client = TextmagicRestClient(usr_pwd.USERNAME, usr_pwd.TOKEN)

    while True:
        current_record = get_record(cfg.COVID_URL) 
        if current_record != {}:
            log_status(current_record, last_record['timestamp'])
            status = get_status(current_record, last_record, SEND_INITIAL_MESSAGE)
            SEND_INITIAL_MESSAGE = False
            if status in ('new', 'changed'):
                # publish_timestamp = cfg.TIMEZONE.localize(publish_timestamp)
                message = get_message(current_record, status)
                recipients = get_recipients(status)
                if recipients > '' and message > '':
                    send_message(recipients, message)
                else:
                    # todo: send error message to recipients having the send_error flag
                    pass
            last_record = current_record.copy()

        else:
            print(f'{datetime.now()} : no data found!')
        time.sleep(FREQUENCY_SECS)