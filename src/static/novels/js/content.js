$(document).ready(function () {

    var page_btn_pre = $("div.pre_next > a:nth-child(1)");
    var page_btn_next = $("div.pre_next > a:nth-child(2)");
    var page_title = $("title");
    var page_chapter_name = $("#content_name");
    // var page_chapter_content = $(".show-content>div");//正文
    var page_chapter_content = $($(".show-content").children("*").get(0)); //正文
    var page_bookmark = $("#bookMark");//书签，需要修改样式
    var page_url = $("#url");//页面隐藏表单，本页地址

    function get_chapter(n_url) {
        $.ajax({
            //提交数据的类型 POST GET
            type: "GET",
            //提交的网址
            url: n_url,
            //提交的数据
            data: {is_ajax: "quickReading_cache"},
            //返回数据的格式
            datatype: "json",//"xml", "html", "script", "json", "jsonp", "text".
            //在请求之前调用的函数
            //beforeSend:function(){$("#msg").html("logining");},
            //成功返回之后调用的函数
            success: function (data) {
                if (typeof data.name == "undefined") {

                } else { // 正确获取到数据
                    var obj = {
                        url: data.url,
                        pre_chapter_url: transform(data.next_chapter)[0],
                        next_chapter_url: transform(data.next_chapter)[1],
                        name: data.name,
                        novels_name: data.novels_name,
                        content: data.soup,
                        bookmark: data.bookmark,
                        chapter_url: data.chapter_url
                    };
                    store(n_url, obj);
                }
            },
            //调用执行后调用的函数
            complete: function () {

            },
            //调用出错执行的函数
            error: function () {
                //请求出错处理
            }
        });
    }

    function transform(obj) {
        var arr = [];
        for (var item in obj) {
            arr.push(obj[item]);
        }
        return arr;
    }

    function store(n_url, obj) {
        window.sessionStorage.setItem(n_url, JSON.stringify(obj));
    }

    function ajax_content_init() {
        if (isSupport()) {
            log("支持sessionStorage，将为你开启页面缓存");
            search_url = window.location;
            // 来自书签页面的跳转不进行缓存
            if (search_url.search.indexOf("from_bookmarks") > 0) {
                log('来自书签页面的跳转不进行缓存')
            } else {
                ajax_task();
                page_bookmark.bind("click", function () {
                    cache_reset();
                });
            }
        } else {
            //不支持
            return;
        }
    }

    function ajax_task() {
        store_query();//检查是否已缓存
        page_btn_pre.unbind("click");
        page_btn_pre.click(function () {
            event.preventDefault();
            if (window.sessionStorage.getItem(page_btn_pre.attr("href")) === null) {
                //若未缓存
                window.location.href = page_btn_pre.attr("href");
            } else {
                try {
                    load(page_btn_pre.attr("href"));
                } catch (err) {
                    window.location.href = page_btn_pre.attr("href");
                }

            }
        });
        page_btn_next.unbind("click");
        page_btn_next.click(function () {
            event.preventDefault();
            if (window.sessionStorage.getItem(page_btn_next.attr("href")) === null) {
                //若未缓存
                window.location.href = page_btn_next.attr("href");
            } else {
                try {
                    load(page_btn_next.attr("href"));
                } catch (err) {
                    window.location.href = page_btn_next.attr("href");
                }

            }
        });
    }


    function load_bookmark(data) {
        page_bookmark.removeClass("bookMark");
        page_bookmark.removeClass("bookMarkAct");
        //log(data.bookmark);
        if (data.bookmark == 0) {
            page_bookmark.addClass("bookMark");
        } else {
            page_bookmark.addClass("bookMarkAct");
        }
    }

    function load_hiddenForm(data) {
        page_url.val(data.url);
    }

    function load_title(data) {
        page_title.html(data.name + " - quickreading");
    }

    function stripscript(s) {//用于过滤script标签
        return s.replace(/<script>.*?<\/script>/ig, '').replace(/<.*?div.*?>/, '');
    }

    function load_chapter_content(data) {
        page_chapter_content.html(stripscript($(data.content).html()));
    }

    function load_chapter_name(data) {
        page_chapter_name.text(data.name);
    }

    function load_btn_href(data) {
        page_btn_pre.attr("href", "/quickreading_content?url=" + data.pre_chapter_url + "&chapter_url=" + data.chapter_url + "&novels_name=" + data.novels_name);
        page_btn_next.attr("href", "/quickreading_content?url=" + data.next_chapter_url + "&chapter_url=" + data.chapter_url + "&novels_name=" + data.novels_name);
    }

    function load_location_url(data) {
        var th_url = window.location.href + "";
        var pos = th_url.indexOf("/quickreading_content?");
        var td_url = "/quickreading_content?url=" + data.url + "&name=" + data.name + "&chapter_url=" + data.chapter_url + "&novels_name=" + data.novels_name;
        th_url += td_url;
        //log(th_url);
        window.history.replaceState({}, data.name + " - quick reading", td_url);
    }

    function load(index) {//从缓存中加载内容
        var data = JSON.parse(window.sessionStorage.getItem(index));
        load_bookmark(data);
        load_hiddenForm(data);
        load_title(data);
        load_chapter_content(data);
        load_chapter_name(data);
        load_btn_href(data);
        load_location_url(data);
        $("body > div.container.all-content > div.move > div.move_up").click();//回到顶部
        ajax_task();
    }


    function store_query() {
        var pre_url = page_btn_pre.attr("href");
        var next_url = page_btn_next.attr("href");
        //log(pre_url);
        //log(window.sessionStorage.getItem(pre_url));
        if (window.sessionStorage.getItem(pre_url) === null) {
            get_chapter(pre_url);
        }
        if (window.sessionStorage.getItem(next_url) === null) {
            get_chapter(next_url);
        }
    }

    function cache_reset() {
        window.sessionStorage.clear();
        ajax_task();
    }


    function isSupport() {
        if (typeof window.sessionStorage == "undefined") { //判断是否支持sessionStorage
            return false;
        }
        return true;
    }


    function log(s) {
        if (1) {
            console.log(s);
        }

    }


    ajax_content_init();


    //按键事件
    $(document).keydown(function (event) {
        var e = event || window.event;
        var k = e.keyCode || e.which;
        switch (k) {
            case 39:
                // right
                page_btn_next.click();
                break;
            case 37:
                // left
                page_btn_pre.click();
                break;
            case 38:
                //	up
                break;
            case 40:
                // down
                break;
        }
        return true;
    });

    // (function(){
    // 	var startX,startY,endX,endY;
    // 	var el = document.querySelector("body");
    // 	//获取点击开始的坐标
    // 	el.addEventListener("touchstart", function (e){
    // 		startX = e.touches[0].pageX;
    // 		startY = e.touches[0].pageY;
    // 	});
    // 	//获取点击结束后的坐标
    // 	el.addEventListener("touchend", function(e){
    // 		endX = e.changedTouches[0].pageX;
    // 		endY = e.changedTouches[0].pageY;
    // 		var x = (endX - startX);
    // 		var y = (endY - startY);
    // 		if(Math.abs(x/y)>5&&Math.abs(x)>30){
    // 			if(x<0){
    // 				page_btn_next.click();
    // 			}else{
    // 				page_btn_pre.click();
    // 			}
    // 		}
    //
    // 	});
    // })();
});


//---------------------------------------------------------------------------------------