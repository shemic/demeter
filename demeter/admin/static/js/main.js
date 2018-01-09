if (typeof(cur) == "undefined" && parent.config.cur) {
	cur = parent.config.cur
}
var editors = [];

function msg(value) {
	if (!value.data) {
		value.data = value.msg;
	}
	var url = '';
	if (value.data != 'reload' && value.status == 2) {
		out(value.msg);
		return;
	} else if(value.data == 'reload') {
		jump('');
	} else {
		if($("#url").length) {
			url = $("#url").val();
		} else {
			out(value.msg);
			return;
		}

		if (url) {
			jump(url);
		} else {
			jump('');
		}
	}
	
	return;
}
function selectShow(e, id, prefix) {
	if (!prefix) {
		prefix = 'update';
	}
 	id = '#'+prefix+'_' + id
	if ($(id).length) {
		$(id).find('option').each(function()
		{
			var parent = $(this).attr('parent');
			if (parent != e.val()) {
				$(this).html('');
				$(this).attr('selected', false)
				$(this).hide();
			} else {
				$(this).html($(this).attr('name'));
				$(this).show();
			}
		})
	}
}
function setFarm(e, id) {
	//$(".top-hide").attr('class', '').show();
	//e.attr('class', 'top-hide'). hide()
	//$("#top-show").html(e.html());
	request('post', '/admin/setCookie', {'farm':id}, function(msg)
    {
    	location.reload()
    });
}
function jump(url) {
	if (typeof(parent.config.parentTitle) == "undefined") {
		if (url) {
			parent.location.href = url
		} else {
			parent.location.reload()
		}
	} else {
		if (url) {
			location.href = url
		} else {
			location.reload()
		}
	}
}
function load(e) {
	var param = eval('(' + e.html() + ')');
	var load = e.attr('load-args');
	if (load) {
		var args = eval('(' + load + ')');
	}
	
	var html = '';
	switch (param.method) {
		case 'showPage':
			e.html(param.name);
			var i;
			var arg = '?'
			for (i in args) {
				arg += '&' + i + '=' + args[i]
			}
			e.click(function()
			{
				showPage(param.url + arg);
			});
			e.attr('class', 'layui-btn layui-btn-normal layui-btn-mini').show()
			break
		case 'showData':
			args.key = param.key
			request('post', param.url, args, function(msg)
	        {
	        	e.html(msg)
	        	e.show()
	        });
			break
	}
}
function out(msg) {
	layer.msg(msg, {icon: 5, anim: 6});
}
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
function notice(msg) {
    layer.msg(msg,{icon:1,time:1000});
}
function show(title, url, w, h, full) {
    x_admin_show(title, url, w, h, full)
}
function del(obj, id, url) {
    layer.confirm('确认要删除吗？',function(index){
    	data = {}
    	data.id = id
       	request('delete', url, data, function(msg)
        {
        	$(obj).parents("tr").remove();
    		notice('已删除');
        })
    });
}

function rec(obj, id, url) {
    layer.confirm('确认要恢复吗？',function(index){
    	data = {}
    	data.id = id
    	data.state = 'True'
       	request('delete', url, data, function(msg)
        {
        	$(obj).parents("tr").remove();
    		notice('已恢复');
        })
    });
}

function delAll() {
    layer.confirm('确认要删除吗？',function(index){
        //捉到所有被选中的，发异步进行删除
        notice('删除成功');
    });
}

function request(type, url, data, callback) {
	data._xsrf = getCookie("_xsrf");
	$.ajax({
		type:type,
		url:url,
		data:data,
		success:function(msg){
		    callback(msg)
		}
	});
}

//跳转页面
function showPage(url) {
	location.href = url
}

function initEditor()
{
	if ($('.layui-editor').length) {
		$ ('.layui-editor').each(function() {
			var parent = $(this).parent().parent();
			loadEditor($(this));
		})
	}
}
function loadEditor(e)
{	
	if (!e.length) {
		return;
	}
	var id = e.attr('id');
	var key = e.attr('key');
	var toolbar = [
	  'title'
	  ,'bold'
	  ,'italic'
	  ,'underline'
	  ,'strikethrough'
	  ,'fontScale'
	  ,'color'
	  ,'ol'
	  ,'ul'
	  ,'blockquote'
	  ,'code'
	  ,'table'
	  ,'link'
	  ,'image'
	  ,'hr'
	  ,'indent'
	  ,'outdent'
	  ,'alignment'
	  , '|'
	  ,'html'
	];

	if (typeof(editors[id]) == "object") {
		editors[id].destroy();
		editors[id] = undefined;
	}

	if (typeof(editors[id]) == "undefined") {
		var xsrf = getCookie("_xsrf");
        var uploadUrl = '/upload?_xsrf='+xsrf;
		editors[id] = new Simditor( {
			textarea: e,
			upload: {
				url: uploadUrl,
				params: {key:key},
				fileKey: 'file',
				connectionCount: 10,
				leaveConfirm: 'Uploading is in progress, are you sure to leave this page?'
			},
			toolbar : toolbar
        });
	}
}