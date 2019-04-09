import os
import sys
import uuid
import pandas as pd
from flask import Flask
from web4note.secret import SECRET_APP_KEY, HOME_MAC, WORK_MAC


if sys.platform.startswith('win'):
    db_prefix = 'sqlite:///'
else:
    db_prefix = 'sqlite:////'

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
        SECRET_KEY=SECRET_APP_KEY,
        SESSION_TYPE = 'filesystem',
    )

    
if uuid.getnode() == HOME_MAC: 
    note_dir = "D:/Share/note7web" # home
    new_note_dir = "D:/Share/notebook/draft"
elif uuid.getnode() == WORK_MAC: 
    note_dir = "E:/Share/Note7Web" # work
    new_note_dir = "E:/Share/notebook/draft"
    # note_dir = "E:/Share/test/bb" # work test
    # new_note_dir = "E:/Share/test/aa"
else:
    note_dir = new_note_dir = ""
    print("不是我的电脑：", uuid.getnode())
NOTEROOT = note_dir
NEWNOTEDIR = new_note_dir
TEMPLIST = "./index.json"
    
from web4note import views