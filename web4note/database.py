import os
from datetime import datetime
import pandas as pd

class Note():
    def __init__(self, root, tp, idx):
        self.root = root
        self.type = tp
        self.id = idx
        self.index = os.path.join(root,"Index/Note_index.json") # 注意win \ 与 / 的不同写法，否则出现'unicodeescape' codec can't decode bytes错误
        self.title = "欢迎"
        self.keywords = ""
        self.ctime = datetime.now()
        self.info_path = False
    
    def getIndexSeries(self):
        self.index_series = pd.read_json(self.index, convert_dates=["atime","ctime","mtime"])
        
    def read(self):
        self.path = f"{self.root}/{self.type}/{self.id}/"
        try:
            for f in os.listdir(self.path):
                path = os.path.join(self.path, f)
                if os.path.isfile(path):
                    if os.path.splitext(f)[1] != ".info":
                        self.filename = f
                        self.atime = datetime.fromtimestamp(os.path.getatime(path))
                        self.ctime = datetime.fromtimestamp(os.path.getctime(path))  # ctime 在unix和win上表示的意义不全相同，不一定是create time也可能是change time
                        self.mtime = datetime.fromtimestamp(os.path.getmtime(path))
                    else:  # read json
                        self.infoname = f
                        info = pd.read_json(path, typ="Series") 
                        self.title = info["title"]
                        self.url = info["url"]
                        self.cat = info["cat"]
                        self.keywords = info["keywords"]
                        self.summary = info["summary"]
                else: # read attachment
                    pass
        except Exception as e:
            print("读取笔记错误",e)




