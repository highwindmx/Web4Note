import os
import pandas as pd
from flask import (render_template, send_from_directory, session, g, request, redirect, url_for)
from web4note import (app, NOTEROOT) 
from web4note.database import Note

@app.route('/')
@app.route('/index')
def index():
    session["user"] = { 'nickname': 'Maokk' }
    note = Note(NOTEROOT, "about", "0")
    note.getIndexSeries()
    note_list = note.index_series
    page = render_template("interface.html"
                          ,title = 'Home'
                          ,noteslist = note_list.head() 
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
    #
    note.getIndexSeries()
    note_list = note.index_series
    #
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
    