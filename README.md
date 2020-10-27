# covid-info-sms
This application checks for the new covid-19 status and sends an sms message to a list of recipients with the most up to date results. In order to use this application for your own purposes, you need to:
- install the python package `textmagic` using pip: 
    > pip install textmagic   
    or: > pip install -r requirements.txt
- Create an account on https://www.textmagic.com/. You can get a free trial account to start with. Generate a token and copy to the configuration (see below)  
- The configuration file contains personal information for the textmagic account, it is therefore not made available on github and needs to be created. Add a file `config.py` with the following content. The fields USERNAME, TOKEN, PHONES must be adjusted for your personal use.

```
USERNAME = "your_textmagic_username"
TOKEN = "textmagic_token"
PHONES = "+4179174xxxx,+4178716xxxx,+4179876xxxx" # comma separated list
COVID_URL = "https://data.bs.ch/api/records/1.0/search/?dataset=100073&q=&rows=1&sort=timestamp&facet=timestamp"
TEXT_TEMPLATE = "ℹ️ Neuste COVID-19 Zahlen, Kanton BS ({}): neue Fälle: {}, Gestorbene: {}. Alle Zahlen unter https://data.bs.ch/explore/dataset/100073/table/?sort=timestamp"
```