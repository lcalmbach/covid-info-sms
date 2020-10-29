# covid-info-sms
This application checks for the new covid-19 status and sends an sms message to a list of recipients with the most up to date results. In order to use this application for your own purposes, you need to:
- install the python package `textmagic` using pip: 
    > pip install textmagic   
    or: > pip install -r requirements.txt
- Create an account on https://www.textmagic.com/. You can get a free trial account to start with. Generate a token and copy to the configuration (see below)  
- The configuration file contains personal information for the textmagic account, it is therefore not made available on github and needs to be created. Add a file `config.py` with the following content. The fields USERNAME, TOKEN, must be adjusted for your personal use.

```
USERNAME = "your_textmagic_username"
TOKEN = "textmagic_token"
PHONES = "+4179174xxxx,+4178716xxxx,+4179876xxxx" # comma separated list
COVID_URL = "https://data.bs.ch/api/records/1.0/search/?dataset=100073&q=&rows=1&sort=timestamp&facet=timestamp"
TEXT_TEMPLATE = "ℹ️ Neuste COVID-19 Zahlen, Kanton BS ({}): neue Fälle: {}, Gestorbene: {}. Alle Zahlen unter https://data.bs.ch/explore/dataset/100073/table/?sort=timestamp"
```
- Create a recipients.txt file and enter the names and mobile phone numbers of all recipients separated by a `;`. Example:   
```
Walter Smith;+33791742111
Jane Doe;+41783169633
Abraham Linkcoln;+41719032345
```

The program is called as `>python covid_info_sms.py <secs> <startdatetime>` where:   
- <secs>: eg. 300 number of seconds between checks in seconds, if new files are available
- <startdatetime>: e.g. '2020-10-29 16:00': start comparison date. If the timestamp of the most up to date covid record is found to be more recent than this timestamp, a message is sent to all recipients. If no date is entered, 2020-01-01 is the default value in which case the most recent record is always more recent and an sms message is always sent with the most current record. After sending the sms, the comparison date is set to the timestamp of the most current record and the sending of sms messages will only be triggered if a new record with a more recent timestamp is found. the startdate only controls, whether a message is sent immediately of if the program waits for the next record update.