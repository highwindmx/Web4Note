import os
from datetime import datetime
import shutil
import pathlib
import uuid
import pandas as pd
from send2trash import send2trash
from bs4 import (BeautifulSoup, Comment)
import lxml # 不一定用，但与bs4解析网页时相关模块有联系，作为模块预装的提示吧

def getDir(dir):
    d = os.path.abspath(dir)
    if not os.path.exists(d):
        os.makedirs(d) # 不同于mkdir 这个方法可以巢式新建文件夹
    return d

class Note():
    def __init__(self, root, cols):
        self.root = root
        self.index_cols = cols
        for d in ["Index","Draft","Archive","Trash"]:
            getDir(os.path.join(root, d))
        self.index_path = os.path.join(root, "Index/Note_index.json")
        self.createIndex()
    
    def createIndex(self):
        if os.path.exists(self.index_path):
            self.readIndex()
        else:
            self.index = pd.DataFrame(columns=self.index_cols)
            self.writeIndex()
    
    def writeIndex(self):
        try:
            self.index.to_json(self.index_path, orient='split') #可以保持读取json内容的顺序
        except Exception as e:
            print("索引表保存出错：", e)
            
    def readIndex(self):
        try:
            self.index = pd.read_json(self.index_path, convert_dates=["atime","ctime","mtime"], orient='split')
            self.index_update_time = datetime.fromtimestamp(os.path.getmtime(self.index_path))
        except Exception as e:
            print("索引表读取出错：", e)
    
    def archiveIndex(self):
        archive_dir = getDir(os.path.join(self.root, "Index/Note_archive"))
        tstmp = str(datetime.timestamp(datetime.now()))
        archive_name = f"({tstmp})".join(os.path.splitext(os.path.basename(self.index_path)))
        #if not os.path.exists(self.index):
        # 万一索引表被误删除时增加鲁棒性
        try:
            shutil.copy(self.index_path, os.path.join(archive_dir, archive_name))
        except Exception as e:
            print("索引表存档出错：", e)
        else:
            self.createIndex()
  
    def add2Index(self):
        self.index.loc[self.id] = self.info

    def sortIndex(self, mode): 
        ds = self.index.loc[self.index['type']==mode].copy()
        ds.sort_values(by='title', inplace=True)
        return ds
        
    #############################        
    def createContent(self):
        self.content = f"<!DOCTYPE html><html><meta charset='utf-8'><head><title>{self.title}</title></head>"
        self.content += f'<body>文件生成于{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}，请开始记录吧</body></html>'
    
    def writeContent(self):
        try:
            f = open(self.content_path, "w", encoding="utf-8")
            f.write(self.content)
        except Exception as e:
            print("内容写入出错：", e)
        else:
            f.close()
    
    def readContent(self):
        # if self.ext == ".html"
        codecs= ("utf-8", "gb18030", "ASCII")
        i = 0
        for codec in codecs:
            try:
                f = open(self.content_path, "r", encoding=codec)
                self.content = f.read()
            except UnicodeDecodeError:
                print("{}按{}读取错误".format(self.content_path, codec))
                self.content = ""
            else:
                # print("按{}读取成功".format(codec)
                i = 1
                f.close()
            if i==1:
                break
    
    def parse(self, p):
        [self.title, self.ext] = os.path.splitext(self.content_name)
        name_s = self.content_name.split("(")[0]
        if not name_s: # != ""
            self.title = name_s  # 这个和singleFile保存的文件名格式有关  
        self.atime = datetime.fromtimestamp(os.path.getatime(p))
        self.ctime = datetime.fromtimestamp(os.path.getctime(p))  
        # ctime 在unix和win上表示的意义不全相同，不一定是create time也可能是change time
        self.mtime = datetime.fromtimestamp(os.path.getmtime(p))     
        self.url = pathlib.Path(os.path.abspath(self.path)).as_uri()   
        # 注意目前只对html有进一步的解析        
        if (self.ext == ".html"):
            self.readContent()
            if not self.content:
                print("未能成功读取HTML文件:", self.content_path)
            else:
                soup = BeautifulSoup(self.content, 'lxml')
                # 摘取标题
                try:
                    self.title = soup.find('h2',{"class":"rich_media_title"}).string.strip()
                except:
                    pass            
                # 摘取URL
                try:
                    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
                    url_p = comments[0].split("url:")[1].split("saved date:")[0].strip()
                except:
                    pass
                else:
                    if url_p[:4] == "http": # 修正部分以前一些本地笔记重新用singleFile保存的链接为file://开头
                        self.url = url_p
                # 摘取分类
                try:
                    self.keywords = soup.title.string.strip()
                except:
                    pass # self.keywords = "未分类"
                else:
                    if (self.keywords == self.title) | (self.keywords == None):
                        self.keywords = "未分类"
        else: # 对于可能是图片或者pdf格式的各类非html笔记
            pass
    
    #############################     
    def createInfo(self):
        self.info = pd.Series([self.type, self.title, self.path, self.ctime, self.mtime, self.atime\
                              ,self.url, self.ext, self.keywords]
                              ,index=self.index_cols)
        # self.data = pd.DataFrame()
        # self.data = self.data.append(self.info, ignore_index=True)
        # self.data.index=[self.id]
        # print(self.data)
        
    def writeInfo(self):
        try:    
            self.info.to_json(self.info_path)
        except Exception as e:
            print("信息写入出错：", e)
    
    def readInfo(self):
        #self.info = pd.read_json(self.info_path, typ="Series") 
        self.info = pd.read_json(self.info_path, typ="Series", convert_dates=["atime","ctime","mtime"])
        self.title = self.info["title"] #.loc[self.id]
        self.url = self.info["url"]
        self.keywords = self.info["keywords"]

    #############################     
    def readAtt(self):
        self.att_path = os.path.join(self.path, "附件")
        try:
            al = os.listdir(self.att_path)
        except Exception as e:
            print("读取附件失败：", e)
        else:
            self.att_list = al

    # addAtt
    # delAtt
    # 
    #############################     
    def create(self, p=None):
        self.id = str(uuid.uuid1())
        self.type = "Draft"
        self.path = os.path.join(self.root, f"{self.type}/{self.id}/")
        while os.path.exists(self.path):
            print("千古奇观啊!居然出现了重复的id", self.id)
            self.id = str(uuid.uuid1())
            self.path = os.path.join(self.root, f"{self.type}/{self.id}/")
        os.makedirs(self.path) # 用getDir()也可以不过体现不出上边循环的作用了
        if not p: # 生成空白的
            self.title = "欢迎"
            self.ctime = datetime.now()
            self.mtime = datetime.now()
            self.atime = datetime.now()
            self.url = ""
            self.ext = ".html"
            self.keywords = ""
            self.att_list = []
            self.createContent()
            self.content_name = f"{self.title}{self.ext}"
            self.content_path = os.path.join(self.path, self.content_name)
            self.writeContent()
        else: # 由已有文件生成
            self.content_name = os.path.basename(p) # 
            self.content_path = shutil.copy2(p, self.path)
            self.parse(self.content_path)
              # 等用于writeContent函数，另外前序函数已进行isfile判断了
        # 新建info文件
        self.createInfo()
        self.info_path = os.path.join(self.path, "{}.info".format(os.path.splitext(self.content_name)[0]))
        # print(self.info_path)
        self.writeInfo()
        # 新建附件文件夹
        os.makedirs(os.path.join(self.path, "附件")) 
        # 新建或更新索引表，意味着索引表就算错了更新，但文件本身不出错就行
        self.index.loc[self.id] = self.info       
    
    def locate(self, tp, idx):
        self.id = idx
        self.type = tp
        self.path = os.path.join(self.root, f"{self.type}/{self.id}/")
        self.read()
    
    def delete(self):
        try:
            send2trash(os.path.abspath(self.path)) 
            # send2trash version1.5版本因为 \ / 符号的问题必须abspath一下, 不然后果很严重！！！
        except Exception as e:
            print("笔记文件夹删除出错",e)
        else: 
            self.index = self.index.drop(self.id)
            self.writeIndex()
    
    def archive(self):
        if self.type == 'Archive':
            print(f"{self.id} {self.title} 已经是存档文件")
        else:
            self.type = 'Archive'
            oldpath = self.path
            self.path = os.path.join(self.root, f"{self.type}/{self.id}/")
            self.createInfo()
            self.writeInfo()
            shutil.move(oldpath, self.path)
            self.index.loc[self.id] = self.info
            self.writeIndex()
    
    def update(self):
        try:
            send2trash(os.path.abspath(self.content_path)) 
        except Exception as e:
            print("笔记删除出错",e)
        else:
            self.content_path = os.path.join(self.path, f"{self.title}{self.ext}")
            self.writeContent()
            self.createInfo()
            self.writeInfo()
            self.index.loc[self.id] = self.info
            self.writeIndex()
        
    def read(self):
        try:
            fl = os.listdir(self.path)
        except Exception as e:
            print("读取笔记错误",e)
        else:
            for f in fl:    
                path = os.path.join(self.path, f)
                if os.path.isfile(path):
                    if os.path.splitext(f)[1] != ".info":
                        self.content_path = path
                        self.content_name = os.path.basename(path)
                        self.ext = os.path.splitext(f)[1]
                        self.readContent()
                    else:  # read json
                        self.info_path = path
                        self.readInfo() # 以后也可以设计先查info，如有问题则重新parse
                else: # read attachment
                    self.readAtt()
                self.atime = datetime.fromtimestamp(os.path.getatime(path))
                self.ctime = datetime.fromtimestamp(os.path.getctime(path))  # ctime 在unix和win上表示的意义不全相同，不一定是create time也可能是change time
                self.mtime = datetime.fromtimestamp(os.path.getmtime(path))    
   #############################################################################         

    # 读取所有旧有的
    # 增加新增的
    def renewIndex(self, mode, newpath):
        self.readIndex() # 获得self.index_update_time
        self.archiveIndex() # 先存档
        def isValidUUID(idstring, version=1):
            try:
                uuid_obj = uuid.UUID(idstring, version=version) 
                # version 好像影响不大？
            except:
                return False
            else:
                return True
        count = 0
        # 载入以前的
        if mode == "all":
            for t in ["Draft", "Archive", "Trash"]:
                l = os.listdir(os.path.join(self.root, t))
                for i in l:
                    self.id = i
                    self.type = t
                    self.path = os.path.join(self.root, f"{self.type}/{self.id}/")
                    if os.path.isdir(self.path) and isValidUUID(self.id):
                        self.read()
                        self.add2Index()
                        count += 1
                        print(f"已加入{count}条笔记")
                    else:
                        print(f"原库中混入：{i}无法添加")
        # 解析新增的
        nl = os.listdir(newpath)
        for nn in nl:
            p = os.path.join(newpath, nn)
            if os.path.isfile(p):
                time_compare1 = (datetime.fromtimestamp(os.path.getatime(p))>self.index_update_time) #.any()
                time_compare2 = (datetime.fromtimestamp(os.path.getmtime(p))>self.index_update_time)
                if (time_compare1 and time_compare2):
                    # print(f"奇怪!居然有之前没导入的混入：{nn}")
                    self.create(p)
                    self.add2Index()
                else:
                    # print(f"旧笔记：{nn}还在暂存笔记库中")
                    self.create(p)
                    self.add2Index()
                count += 1
                print(f"已加入{count}条笔记")    
            else:
                print(f"新增混入：{nn}无法添加")                             
        self.writeIndex()

   #############################################################################   
   
    def searchInIndex(self, data):
        cond = data['cond']
        if data['terms']:
            terms = data['terms'].split("\n")
            ci = self.index.any(axis='columns')
            ca = []
            for t in terms:
                if t or (not t.isspace()): #空字符就不要了
                    ct = self.index['title'].str.contains(t, case=False, na=False)
                    ck = self.index['keywords'].str.contains(t, case=False, na=False)
                    ca.append((ct | ck))
            if cond == 'and':
                cc = ci
                for c in ca:
                    cc = (cc & c)
            if cond == 'or':
                cc = ~ci
                for c in ca:
                    cc = (cc | c)
            if cond == 'not':
                cc = ci
                for c in ca:
                    cc = (cc & ~c)
            #print(self.index[cc]) 
            print(terms, cond)            
        else: # 如果值为空，则进行重复查找
            cc = self.index.duplicated(subset=['title'], keep=False)
        return self.index[cc]    
        
                    
    
    
    


