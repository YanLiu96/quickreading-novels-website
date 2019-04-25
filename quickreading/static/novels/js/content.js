$(document).ready(function () {
    var page_btn_pre = $("div.pre_next > a:nth-child(1)");
    var page_btn_next = $("div.pre_next > a:nth-child(2)");
    var page_title = $("title");
    var page_chapter_name = $("#content_name");
    //main content
    var page_chapter_content = $($(".show-content").children("*").get(0));
    //bookmark
    var page_bookmark = $("#bookMark");
    var page_url = $("#url");

    function get_chapter(n_url) {
        $.ajax({
            type: "GET",
            url: n_url,
            data: {is_ajax: "quickReading_cache"},
            datatype: "json",
            success: function (data) {
                if (typeof data.name == "undefined") {

                } else {
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
            complete: function () {

            },
            //调用出错执行的函数
            error: function () {
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
            log("support sessionStorage，cache page");
            search_url = window.location;
            // 来自书签页面的跳转不进行缓存
            if (search_url.search.indexOf("from_bookmarks") > 0) {
                log('not cache page which open in bookmark')
            } else {
                ajax_task();
                page_bookmark.bind("click", function () {
                    cache_reset();
                });
            }
        } else {
            return;
        }
    }

    function ajax_task() {
        // check whether cache
        store_query();
        page_btn_pre.unbind("click");
        page_btn_pre.click(function () {
            event.preventDefault();
            if (window.sessionStorage.getItem(page_btn_pre.attr("href")) === null) {
                //not cache
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
                //not cache
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

    // delete script
    function stripscript(s) {
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
        window.history.replaceState({}, data.name + " - quick reading", td_url);
    }

    //load data from cache(session)
    function load(index) {
        var data = JSON.parse(window.sessionStorage.getItem(index));
        load_bookmark(data);
        load_hiddenForm(data);
        load_title(data);
        load_chapter_content(data);
        load_chapter_name(data);
        load_btn_href(data);
        load_location_url(data);
        $("body > div.container.all-content > div.move > div.move_up").click();
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


    //support keyboard up and down
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

});