$(document).ready(function () { 
    // 加载后变色
    window.onload = function(){ //用这种办法可以避免第一次执行要点两次的问题
        var btn_e = document.getElementById("edit-btn");
        btn_e.style["background-color"] = 'lightgreen';
        var btn_v = document.getElementById("view-btn");
        btn_v.style["background-color"] = 'lightblue';
        frames['wysiwyg'].document.designMode = 'on';
    };
    // 存档用的脚本
    $('#arch-btn').click(function() {
        var note_t = document.getElementById("note-title").value;
        var note_k = document.getElementById("note-keywords").value;
        var note_c = frames["wysiwyg"].document.documentElement.outerHTML;
        var data = {};
        data['content'] = note_c
        data['title'] = note_t
        data['keywords'] = note_k
        $.ajax({
            type: 'POST',
            url: "/_archive",
            data: JSON.stringify(data),
            dataType: 'json', // 注意：这里是指希望服务端返回json格式的数据
            contentType:'application/json; charset=utf-8',
            success: function(data) { 
                //console.log("cool", data)
            },
            error: function(xhr, type) {
                //console.log("notcool", data)
            }
        });
    });
    // 删除用的脚本
    $('#dele-btn').click(function() {
        var note_t = document.getElementById("note-title").value;
        var note_k = document.getElementById("note-keywords").value;
        var note_c = frames["wysiwyg"].document.documentElement.outerHTML;
        var data = {};
        data['content'] = note_c
        data['title'] = note_t
        data['keywords'] = note_k
        $.ajax({
            type: 'POST',
            url: "/_delete",
            data: JSON.stringify(data),
            dataType: 'json', // 注意：这里是指希望服务端返回json格式的数据
            contentType:'application/json; charset=utf-8',
            success: function(data) { 
                //console.log("cool", data)
            },
            error: function(xhr, type) {
                //console.log("notcool", data)
            }
        });
        $("#note-del-alt").slideDown(); //顶部浮动提示
    });
    // 保存用的脚本 
    $('#save-btn').click(function() {
        var note_t = document.getElementById("note-title").value;
        var note_k = document.getElementById("note-keywords").value;
        var note_c = frames["wysiwyg"].document.documentElement.outerHTML;
        var data = {};
        data['content'] = note_c
        data['title'] = note_t
        data['keywords'] = note_k
        $.ajax({
            type: 'POST',
            url: "/_save",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType:'application/json; charset=utf-8',
            success: function(data) { 
                //console.log("cool", data)
            },
            error: function(xhr, type) {
                //console.log("notcool", data)
            }
        });
    });
    // 修饰笔记用
    $('.WYSIWYG-button').each(function() {
        if (this.id === "view-btn"){
            $(this).on("click", function() {
                frames['wysiwyg'].document.designMode = 'off';
                //console.log(666)    
            });
        } else if(this.id === "edit-btn"){
            $(this).on("click", function() {
                frames['wysiwyg'].document.designMode = 'on';   
            });
        } else {
            $(this).on("click", function() {
                frames['wysiwyg'].document.designMode = 'on';
                frames['wysiwyg'].document.execCommand(this.getAttribute('data-name'), false, this.getAttribute('data-value'));
            });           
        };
    });
});    
