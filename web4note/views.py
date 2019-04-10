import os
import pandas as pd
import numpy as np
from flask import (render_template, send_from_directory, url_for, session, g, jsonify, json, request, redirect)
from web4note import (app, NOTEROOT, NEWNOTEDIR)#, TEMPLIST) 
from web4note.database import Note

NOTEINDEXCOLS= ["type","title","path","ctime","mtime","atime"
               ,"url","ext","keywords"]

# 笔记更新追加功能还未完成！！！

# 附件相关功能还没有设计完成！！！
# 日历未完成
# 高级查找，查找重复
               
@app.route('/')
@app.route('/index')
@app.route('/table')
def index():
    note = Note(NOTEROOT, NOTEINDEXCOLS)
    note.getUpdateTime() 
    session['update_time'] = note.index_update_time 
    # 暂存更新时间（以打开笔记本时为准），防止后续读写index导致更新时间有误
    note.readIndex()
    note.doStatistics()
    countinfo = f"所有：{note.index.shape[0]}\
                  草稿：{note.index.loc[note.index['type']=='Draft'].shape[0]}\
                  存档：{note.index.loc[note.index['type']=='Archive'].shape[0]}"
    page = render_template("index.html" 
                          ,title = '索引页 - 网页笔记本'
                          ,note_root = NOTEROOT 
                          ,note_new_dir = NEWNOTEDIR
                          ,note_update_time = session['update_time']
                          ,note_count = countinfo
                          )
    return page

@app.route('/_get_table')
def getTable():
    note = Note(NOTEROOT, NOTEINDEXCOLS)
    note.readIndex()
    # 导入并规整加载到表格里的数据格式
    df = note.index
    df['title'] = "<a href='load/"+ df['type'] + "/" + df.index + "'>" + df['title'] + "</a>"    # 改造title使之超链接化 
    df['atime'] = df['atime'].apply(lambda x: x.strftime('%Y-%m-%d')) # 日期格式化
    df['ctime'] = df['ctime'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df['mtime'] = df['mtime'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df = df[['type','ext','title','mtime','atime','ctime','keywords']] # 忽略path url，同时调整顺序
    dj = df.to_json(orient="split") # orient="split" 可能和后边的json.loads有关！！！
    #print(dj)
    return jsonify(note_list=json.loads(dj)["data"],
                   columns=[{"title": str(col)} for col in json.loads(dj)["columns"]])

@app.route('/load/<string:tp>/<string:idx>')
def load(tp, idx):
    # print(tp, idx)
    session['type'] = tp
    session['id'] = idx
    note = Note(NOTEROOT, NOTEINDEXCOLS)
    note.locate(session['type'], session['id'])
    page = render_template("edit.html"
                          ,title = '笔记页'
                          ,noteinfo = note
                          ,source= url_for('sendPage')  # 采用这种方法使得本不能加载本地网页的iframe重新可用
                          )
    return page
    
@app.route('/_get_page')
def sendPage():
    note = Note(NOTEROOT, NOTEINDEXCOLS)
    note.locate(session['type'], session['id']) 
    note.read()
    # 虽然session不接受dataframe格式，但是可以通过session在函数间共享当前笔记的id和type，然后再locate，模拟数据库的功能
    return send_from_directory(note.path, note.content_name) # 采用这种方法使得本不能加载本地网页的iframe重新可用

@app.route('/_delete')
def delete():
    note = Note(NOTEROOT, NOTEINDEXCOLS)
    note.locate(session['type'], session['id'])
    fname = note.content_name
    note.delete()
    page = render_template("update.html" ,title = '删除后 - 网页笔记本' ,info = f"已删除笔记: {fname} ") # update.html与index.html共享使用table.html
    return page

@app.route('/_archive', methods=["POST"])
def archive():
    data = request.get_json() # print("保存内容",data)
    #
    note = Note(NOTEROOT, NOTEINDEXCOLS)
    note.locate(session['type'], session['id'])
    #
    note.title = data['title']
    note.keywords = data['keywords']
    note.content = data['content']
    note.update("Archive")
    return "存档完毕"

@app.route('/_save', methods=["POST"])
def save():
    data = request.get_json() # 接收js传递来的数据
    note = Note(NOTEROOT, NOTEINDEXCOLS)
    note.locate(session['type'], session['id'])
    #
    note.title = data['title']
    note.keywords = data['keywords']
    note.content = data['content']
    note.update("Save")
    return "保存完毕"   

@app.route('/_update', methods=["POST"])
def update():
    data = request.get_json()
    if data["mode"] in ["all", "new"]:
        note = Note(NOTEROOT, NOTEINDEXCOLS)
        note.renewIndex(data["mode"], NEWNOTEDIR)
    else:
        print(f"unknown mode: {data['mode']}")
    return "更新完毕"    