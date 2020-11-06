# covid-info-sms
This application checks for the new covid-19 status and sends an sms message to a list of recipients with the most up to date results. In order to use this application for your own purposes, you need to:
- install the python package `textmagic` using pip: 
    > pip install textmagic   
    or: > pip install -r requirements.txt
- Create an account on https://www.textmagic.com/. You can get a free trial account to start with. Generate a token and copy to the configuration (see below)  
- The configuration file contains personal information for the textmagic account, it is therefore not made available on github and needs to be created. Add a file `usr_pwd.py` with the following content. The fields USERNAME, TOKEN, must be set to the values provided by your textmagic account.

```
USERNAME = "your_textmagic_username"
TOKEN = "textmagic_token"
```
- Create a recipients.txt file and enter the names and mobile phone numbers and the flags for when to send messages of all recipients separated by a `;`. Example:   
    ```
    name;mobile;send_new;send_update;send_error
    Walter Smith;+33791742111;0;0;1
    Jane Doe;+41783169633;1;1;0
    Abraham Linkcoln;+41719032345;1;0;0
    ```
    where:   
    - send_new: text when a new record is encountered (new timestamp)
    - send_updates: text if any field except the timestamp in the last record was changed
    - send_error: send text if error occurred in the application (should only be admin, W. Smith in the example)


The program is called as 
```  
>python covid_info_sms.py <secs> <send_initial_msg>
```   
where:   
- `secs`: eg. 300 number of seconds between checks in seconds, if new files are available. Optional, Default is 300
- `send_initial_msg`: True if you wish to force a message when starting the app, this can be useful for testing, so you dont need to wait for a record update. Optional, default is False.