$(document).ready(function () { //用这种办法可以避免第一次执行要点两次的问题
    //加载表格的脚本
    var table = null;
    $.getJSON('/_get_table', 
        function(data) {
            //console.log(data.columns);
            if (table !== null) {
                table.destroy();
                table = null;
                $("#note_list_table").empty();
            }
            table = $("#note_list_table").DataTable({
                data: data.note_list,
                columns: data.columns
            });
        }
    );    
                       
    // 更新全部用的脚本
    $('#update-all').click(function() {
        var data = {};
        data['mode'] = "all"
        //console.log(data);
        $.ajax({
            type: 'POST',
            url: "/update",
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
    
    // 更新最新用的脚本
    $('#update-new').click(function() {
        var data = {};
        data['mode'] = "new"
        //console.log(data);
        $.ajax({
            type: 'POST',
            url: "/update",
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
    
    // 搜索重置用的脚本
    $('#search-reset-btn').click(function() {
        $('#search-input').val('');
    });
    
    // 搜索用的脚本
    $('#search-btn').click(function() {
        var data = {};
        data['terms'] = $('#search-input').val()
        data['cond'] = $('input[name=search-radio]:checked').val();
        console.log(data);
        $.ajax({
            type: 'POST',
            url: "/search",
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
        //window.location.href="{{ url_for( 'searchResult' ) }}";
    });
});    
