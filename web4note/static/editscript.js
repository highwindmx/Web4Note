$(document).ready(function () { 
    // 加载后变色
    window.onload = function(){ //用这种办法可以避免第一次执行要点两次的问题
        var btn_e = document.getElementById("edit-btn");
        btn_e.style["background-color"] = 'lightgreen';
        var btn_v = document.getElementById("view-btn");
        btn_v.style["background-color"] = 'lightblue';
        frames['wysiwyg'].document.designMode = 'on';
        //console.log(frames['wysiwyg'].src) 
    };
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
