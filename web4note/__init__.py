import os
import sys
import uuid
import pandas as pd
from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
from web4note.secret import SECRET_APP_KEY, HOME_MAC, WORK_MAC


if sys.platform.startswith('win'):
    db_prefix = 'sqlite:///'
else:
    db_prefix = 'sqlite:////'

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
        SECRET_KEY=SECRET_APP_KEY,
        SESSION_TYPE = 'filesystem',
        #SQLALCHEMY_DATABASE_URI=db_prefix + os.path.join(app.root_path, 'note_db.sqlite3'),
        #SQLALCHEMY_TRACK_MODIFICATIONS = False,
    )

#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config.from_pyfile('config.py', silent=True)    
# try:
#     os.makedirs(app.instance_path)
# except OSError:
#     pass
    
if uuid.getnode() == HOME_MAC: # home
    note_dir = "D:/Share/note7web"  # 注意win \ 与 / 的不同写法，否则出现'unicodeescape' codec can't decode bytes错误
elif uuid.getnode() == WORK_MAC: # work
    note_dir = "E:/Share/Note7Web"
else:
    note_dir = ""
    print("不是我的电脑：", uuid.getnode())
NOTEROOT = note_dir
    
from web4note import views