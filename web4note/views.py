import os
import pandas as pd
from flask import (render_template, send_from_directory, session, g, request, redirect, url_for)
from web4note import (app, NOTEROOT) #db, 
from web4note.database import Note

# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.Text)
#     link = db.Column(db.Text)
#     cat = db.Column(db.Text)
#     keywords = db.Column(db.Text)
#     summary = db.Column(db.Text)
#     ctime = db.Column(db.DateTime)
#     mtime = db.Column(db.DateTime)
#     atime = db.Column(db.DateTime)
# 
# db.create_all()
#
@app.route('/')
@app.route('/index')
def index():
    #session['root'], session['index_path'] = initEnv()
    # user = { 'nickname': 'Maokk' }
    session["user"] = { 'nickname': 'Maokk' }
    # pages = render_template("index.html", title = 'Home', user = user, page="notes/demo.html")
    # page = render_template("about.html") 
    # notes_list = pd.read_json(session['index_path'], convert_dates=["atime","ctime","mtime"])
    # session['list'] = notes_list.to_json()
    #notes_list = g.notes_list.head()
    note = Note(NOTEROOT, "about", "0")
    note.getIndexSeries()
    note_list = note.index_series
    page = render_template("interface.html"
                          ,title = 'Home'
                          ,noteslist = note_list.head() # /Draft/000c46ee-3dc6-11e9-9cf9-c82158175d2b
                          #,notetitle = "欢迎"
                          #,notekeywords = ""
                          ,noteinfo = note
                          ,user = session["user"]
                          ,source=url_for("static", filename="about.html"))
    return page

@app.route('/<string:tp>/<string:idx>')
def shownote(tp, idx):
    # 
    note = Note(NOTEROOT, tp, idx)
    note.read()
    session["dir"] = note.path
    session["file"] = note.filename
    note.getIndexSeries()
    note_list = note.index_series
    #        
    #page = render_template("interface.html", title = 'Home', noteslist = notes_list, user = session["user"], source=f"../load/{idx}") 
    # 此时以/<string:cat>/为根故而需要向上一层
    # notes_list = pd.read_json(session['index_path'], convert_dates=["atime","ctime","mtime"])
    # notes_list = notes_list.head()
    #notes_list = pd.read_json(session['list'])
    # notes_list = pd.read_json(session['index_path'], convert_dates=["atime","ctime","mtime"])
    page = render_template("interface.html"
                          ,title = 'Home'
                          ,noteslist = note_list.head()
                          ,noteinfo = note
                          ,user = session["user"]
                          ,source=url_for('loadnote', idx=idx)) 
    
    return page
    
@app.route('/load/<string:idx>')
def loadnote(idx):
    return send_from_directory(session["dir"], session["file"])

# @app.route('/test/<string:idx>')
# def test(idx):
#     user = { 'nickname': 'Test' }
#     #return app.send_static_file("E:\\Share\\Note7Web\\Draft\\00a89710-3455-11e9-ac01-802bf9bf71c6\\学术经纬 (2018-12-27 00_09_33.434).html")
#     # return send_from_directory("E:/Share/Note7Web/Draft/00a89710-3455-11e9-ac01-802bf9bf71c6/","学术经纬 (2018-12-27 00_09_33.434).html")   
#     return render_template("wysiwyg.html", title = 'Home', user = user, source=f"noteid/{idx}")
    
# @app.route('/list')
# def listNotes():
#     #print(noteslist)
#     user = { 'nickname': 'WenJJ' }
#     # notes_list = pd.read_json(session['index_path'], convert_dates=["atime","ctime","mtime"])
#     page = render_template("list.html", title = 'Home', noteslist = NotesList, user = user, source="notes/DrWhy (2019-03-15 06_55_23.108).html")
#     return page