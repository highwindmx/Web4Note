import os
import uuid
from datetime import datetime
import pathlib
import shutil
from send2trash import send2trash
from bs4 import (BeautifulSoup, Comment)
import lxml # 不一定用，但与bs4解析网页时相关模块有联系，作为模块预装的提示吧
import pandas as pd
from wordcloud import WordCloud
import jieba

NOTEINDEXCOLS= ["type","title","path","ctime","mtime","atime"
               ,"url","att_list","att_num","keywords"]
               
def getDir(dir):
    d = os.path.abspath(dir)
    if not os.path.exists(d):
        os.makedirs(d) # 不同于mkdir makedirs方法可以巢式新建文件夹
    return d

class Note():
    """
    ：：：由于混在一起设计了稍微写下省的犯错：：：
    
    self.root = 笔记库根目录
    self.index = 索引表本身
    self.index_cols = 索引中的格列标题
    self.index_path = 索引的保存路径
    self.index_update_time = 索引的更新时间
    
    self.id = id
    # self.ext = 扩展名
    self.title = 标题
    self.type = 分类
    self.keywords = 关键词
    self.path = 笔记文件夹的路径 os.path.join(self.root, f"{self.type}/{self.id}/")
    self.url = 外链
    self.atime = atime access?
    self.ctime = ctime create?
    self.mtime = mtime modify
    self.content = 内容本身
    self.content_name = 内容的文件名 f"{self.title}.html"
    self.content_path = 内容的保存路径
    
    self.info = info内容本身
    self.info_path = info的保存路径
    
    self.att_path = 附件文件夹路径
    
    """
    
    def __init__(self, root):
        self.root = root
        self.index_cols = NOTEINDEXCOLS
        for d in ["Index","Draft","Archive","Trash"]:
            getDir(os.path.join(root, d))
        self.index_path = os.path.join(root, "Index/Note_index.json")
        self.createIndex()
    
    # index ########################      
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
    
    def getUpdateTime(self):
        self.index_update_time = datetime.fromtimestamp(os.path.getmtime(self.index_path))
        
    # def sortIndex(self, mode): 
    #     ds = self.index.loc[self.index['type']==mode].copy()
    #     ds.sort_values(by='title', inplace=True)
    #     return ds
        
    # 内容 ########################        
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
        if not self.content:
            print("未能成功读取HTML文件:", self.content_path)

    # info ##########################     
    def createInfo(self):
        self.readAtt()
        self.info = pd.Series([self.type, self.title, self.path, self.ctime, self.mtime, self.atime\
                              ,self.url, self.att_list, self.att_num, self.keywords]
                              ,index=self.index_cols)
        
    def writeInfo(self):
        self.createInfo()
        self.info_path = os.path.join(self.path, "{}.info".format(os.path.splitext(self.content_name)[0]))
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

    # 附件 #######################
    def addAtt(self, p):
        try:
            new_att = shutil.copy(p, os.path.join(self.path, "附件"))
        except Exception as e:
            print("附件添加错误：",e)
        else:
            self.att_list.append(os.path.basename(new_att))
            self.att_num = len(self.att_list)
    
    def readAtt(self):
        att_path = os.path.join(self.path, "附件")
        try:
            al = os.listdir(att_path)
        except Exception as e:
            print("读取附件失败：", e)
        else:
            self.att_num = len(al)
            # self.att_list = al
            if self.att_num == 0:
                self.att_list = [""]
            else:
                self.att_list = al

    # delAtt
    # 
    # 笔记本身 ########################     
    def create(self, p=None):
        self.id = str(uuid.uuid1())
        self.type = "Draft"
        self.path = os.path.join(self.root, f"{self.type}/{self.id}/")
        while os.path.exists(self.path):
            print("千古奇观啊!居然出现了重复的id", self.id)
            self.id = str(uuid.uuid1())
            self.path = os.path.join(self.root, f"{self.type}/{self.id}/")
        # 新建笔记文件夹
        os.makedirs(self.path) # 用getDir()也可以不过体现不出上边循环的作用了
        # 新建附件文件夹
        os.makedirs(os.path.join(self.path, "附件"))
        self.keywords = "未分类"
        self.att_list = []
        #
        if not p: # 生成空白的
            self.title = "欢迎"
            self.ctime = datetime.now()
            self.mtime = datetime.now()
            self.atime = datetime.now()
            self.url = ""
            self.createContent()
            self.content_name = f"{self.title}.html"
            self.content_path = os.path.join(self.path, self.content_name)
            self.writeContent()
        else:
            [self.title, file_ext] = os.path.splitext(os.path.basename(p))
            self.atime = datetime.fromtimestamp(os.path.getatime(p))
            self.ctime = datetime.fromtimestamp(os.path.getctime(p))  
            # ctime 在unix和win上表示的意义不全相同，不一定是create time也可能是change time
            self.mtime = datetime.fromtimestamp(os.path.getmtime(p))     
            self.url = pathlib.Path(os.path.abspath(self.path)).as_uri()
            #
            if file_ext == ".html":# 开始解析
                self.parseHTML(p)
            else: # 对于可能是图片或者pdf格式的各类非html笔记
                self.createContent()
                self.content_name = f"{self.title}.html"
                self.content_path = os.path.join(self.path, self.content_name)
                self.writeContent()
                self.addAtt(p)
        # 新建info文件
        self.writeInfo()
        # 新建或更新索引表，意味着索引表就算更新错了，但文件本身不出错就行
        self.index.loc[self.id] = self.info
        #self.writeIndex()  否则后边更新新增时会反复读写      
    
    def parseHTML(self,p):
        self.content_name = os.path.basename(p)
        self.content_path = shutil.copy2(p, self.path) # 解析与追加同时进行
        name_s = self.content_name.split("(")[0]
        if not name_s: # != ""
            self.title = name_s  # 这个和singleFile保存的文件名格式有关     
        self.readContent()
        # 开始爬取
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
            print(f"笔记{self.id}删除成功")
     
    def update(self, mode):
        old_content_name = self.content_name    
        send2trash(os.path.abspath(self.info_path))
        # 再移
        if mode=="Archive":    
            if self.type == 'Archive':
                print(f"已经是存档文件: {self.id} {self.title}")
            else:
                self.type = 'Archive'
                oldpath = self.path
                self.path = os.path.join(self.root, f"{self.type}/{self.id}/")
                shutil.move(oldpath, self.path)
        else: # "save"    
            pass
        # 最后改
        self.content_name = f"{self.title}.html"
        self.content_path = os.path.join(self.path, self.content_name)
        send2trash(os.path.abspath(os.path.join(self.path, old_content_name)))
        self.writeContent()
        self.writeInfo()
        # 修改index
        self.index.loc[self.id] = self.info
        self.writeIndex()
        
    def read(self):
        try:
            fl = os.listdir(self.path)
        except Exception as e:
            print("读取笔记错误",e)
        else:
            info_exist = 0
            content_exist = 0
            for f in fl:    
                path = os.path.join(self.path, f)
                if os.path.isfile(path):
                    if os.path.splitext(f)[1] == ".html":
                        content_exist = 1
                        self.content_path = path
                        self.content_name = os.path.basename(path)
                        self.atime = datetime.fromtimestamp(os.path.getatime(self.content_path))
                        self.ctime = datetime.fromtimestamp(os.path.getctime(self.content_path))  # ctime 在unix和win上表示的意义不全相同，不一定是create time也可能是change time
                        self.mtime = datetime.fromtimestamp(os.path.getmtime(self.content_path))
                    elif os.path.splitext(f)[1] == ".info":  # read json
                        info_exist = 1
                        self.info_path = path
                        self.readInfo() # 以后也可以设计先查info，如有问题则重新parse
                    else:
                        print(f"{f}混入了{self.path}")
                else: # read attachment
                    self.readAtt()
            if info_exist == 0: 
                print(f"未成功读取{self.path}的info")
            if content_exist == 0:
                print(f"未成功读取{self.path}的content")
                
   #############################################################################         

    # 重新或追加索引
    def renewIndex(self, mode, newpath):
        self.getUpdateTime() # 获得self.index_update_time
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
                        self.index.loc[self.id] = self.info # 信息加入index
                        count += 1
                    else:
                        print(f"原库中混入：{i}无法添加")
                    if count % 10 == 0:
                        print(f"已加入{count}条笔记")
                    else:
                        pass    
        # 解析新增的
        todo_dir = getDir(os.path.join(newpath,"Draft"))
        done_dir = getDir(os.path.join(newpath,"imported"))
        nl = os.listdir(todo_dir)
        for nn in nl:
            p = os.path.join(todo_dir, nn)
            if os.path.isfile(p):
                time_compare1 = (datetime.fromtimestamp(os.path.getatime(p))>self.index_update_time) #.any()
                time_compare2 = (datetime.fromtimestamp(os.path.getmtime(p))>self.index_update_time)
                if (time_compare1 and time_compare2): # 肯定是新加入摘取的
                    self.create(p)
                    shutil.move(p, done_dir) # 防止之后的重复导入
                    self.index.loc[self.id] = self.info # 信息加入index
                    count += 1
                else: # 疑似已经加入笔记库的了
                    # print(f"疑似旧笔记：{nn} 暂未存入笔记库中")
                    self.create(p)
                    shutil.move(p, done_dir)
                    self.index.loc[self.id] = self.info # 信息加入index
                    count += 1
                if count % 10 == 0:
                    print(f"已加入{count}条笔记")
                else:
                    pass
            else:
                print(f"新增混入：{nn}无法添加")                             
        print(f"共加入{count}条笔记")
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
        
    def doStatistics(self):
        tb = self.index["keywords"]
        text = "/".join(jieba.cut(" ".join(tb)))
        #print(text)
        #print(os.path.abspath("./"))
        try:
            wc = WordCloud(background_color="white"
                          ,font_path="./web4note/static/font/GenWanMinTW-Regular.ttf"
                          ,margin=2
                          ,width=800
                          ,height=400
                          ).generate(text)
        except Exception as e:
            print("词云生成错误：",e)
        else:
            wc.to_file("./web4note/static/images/wordcloud.png") 
    
    
    


