import os
import pandas as pd
import numpy as np
from flask import (render_template, send_from_directory, url_for, session, g, jsonify, json, request, redirect)
from web4note import (app, NOTEROOT, NEWNOTEDIR, TEMPLIST) 
from web4note.database import Note

NOTEINDEXCOLS= ["type","title","path","ctime","mtime","atime"
               ,"url","ext","keywords"]

@app.route('/')
@app.route('/index')
@app.route('/table')
def index():
    page = render_template("index.html" ,title = 'Home - 网页笔记本')
    return page

@app.route('/_get_table')
def getTable():
    # df = pd.DataFrame(np.random.randint(0, 100, size=(a, b)))
    # df = pd.read_json('list2.json')
    # dj = df.to_json(orient="split")
    # print(df)
    note = Note(NOTEROOT, NOTEINDEXCOLS)
    note.readIndex()
    df = note.index # pd.read_json('list1.json', convert_dates=["atime","ctime","mtime"], orient="split")
    df['title'] = "<a href='load/"+ df['type'] + "/" + df.index + "'>" + df['title'] + "</a>" # 改造title使之超链接化
    df['atime'] = df['atime'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df['ctime'] = df['ctime'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df['mtime'] = df['mtime'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df = df[['type','ext','title','mtime','atime','ctime','keywords']]
    dj = df.to_json(orient="split")
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
                          ,title = 'Home'
                          ,noteinfo = note
                          ,source= url_for('sendPage')
                          )
    return page
    
@app.route('/_get_page')
def sendPage():
    note = Note(NOTEROOT, NOTEINDEXCOLS)
    note.locate(session['type'], session['id'])
    #session['dir'] = note.path
    #session['file'] = note.content_name
    return send_from_directory(note.path, note.content_name) # 采用这种方法使得本不能加载本地网页的iframe重新可用

@app.route('/_delete')
def delete():
    note = Note(NOTEROOT, NOTEINDEXCOLS)
    note.locate(session['type'], session['id'])
    fname = note.content_name
    note.delete()
    page = render_template("update.html" ,title = '删除后 - 网页笔记本' ,info = f"已删除笔记: {fname} ")
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
    return "存档完毕" #page

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