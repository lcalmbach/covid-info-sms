"""
covid_info_sms.py retrieves the last opendata.bs-covid record 
(https://data.bs.ch/explore/dataset/100073/table/?sort=timestamp) and checks 
the timestamp. If it is newer than the timestamp when the program was started, 
an sms text is generated with the key values and sent to a list of recipients. 

parameters:
frequency_secs: number of seconds between calls


example:
python covid_alert.py 300
"""

from textmagic.rest import TextmagicRestClient
from datetime import datetime
from urllib.request import urlopen
import pandas as pd
import json
import time
import sys
import config as cfg


__version__ = '0.1.1'

def get_recipients() -> str:
    """
    reads all recipients from a text file and returns a csv-string
    """

    recipients = ''
    try: 
        url = './recipients.txt'
        df_recipients = pd.read_csv(url, sep=';', engine='python', header=None, names=['name','mobile'], dtype=str)
        lst = df_recipients['mobile'].tolist()
        recipients = ','.join(lst)
    except Exception as ex:
        print(f'An error occurred in function get_recipients(): {str(ex)}')
    finally:
        return recipients

def get_record(url:str)-> str:
    result = []
    try: 
        jsonurl = urlopen(url)
        result = json.loads(jsonurl.read())
    except Exception as ex:
        print(f'An error occurred: {str(ex)}')
    return result

def compare_timestamps(date1, date2):
    """
    compares if date1 timestamp is newer than date1 timestamp
    """

    secs_since_last_publication = (date1 - date2).total_seconds()
    return (secs_since_last_publication > 0)

def send_message(recipients: str, text: str):
    """
    sends an sms to all entries in the recipients list.
    """

    try: 
        message = client.messages.create(phones=recipients, text=text)
        print(text)
    except Exception as ex:
        print(f'An error occurred: {str(ex)}')
    
if __name__ == "__main__":
    FREQUENCY_SECS = int(sys.argv[1])
    last_update = datetime.now()
    client = TextmagicRestClient(cfg.USERNAME, cfg.TOKEN)
    
    while True:
        # list of records
        records = get_record(cfg.COVID_URL)
        #fields from frist record
        if len(records) > 0:
            data = records['records'][0]['fields']
            print(data)
            publish_timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S+00:00")
            print(publish_timestamp, last_update)
            if compare_timestamps(publish_timestamp, last_update):
                # publish_timestamp = cfg.TIMEZONE.localize(publish_timestamp)
                date_str = f"{datetime.strftime(publish_timestamp, '%d. %B')} {data['time']}"
                try: 
                    message = cfg.TEXT_TEMPLATE.format(date_str, 
                        data['ndiff_conf'], 
                        data['ndiff_deceased']) 
                        #data['current_hosp']) die liegen erst am Nachmittag vor
                    recipients = get_recipients()
                    if recipients > '':
                        send_message(recipients, message)
                        last_update = datetime.now()
                except Exception as ex:
                    print(f'An error occurred: {str(ex)}')
        time.sleep(FREQUENCY_SECS)

