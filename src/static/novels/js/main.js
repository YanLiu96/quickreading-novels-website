$(function () {
    $('[data-toggle="popover"]').popover()
});


$(document).ready(function () {
    $('.move_up').click(function () {
        $('html, body').animate({scrollTop: 0}, 'slow');
        return false;
    });
    $('.move_down').click(function () {
        $('html, body, .content').animate({scrollTop: $(document).height()}, 300);
        return false;
    });
    // book
    $('#owllook_book').click(function () {
        var chapter_url = $("#chapter_url").val();
        var novels_name = $("#novels_name").val();
        if ($(this).hasClass('add-color')) {
            // delete book
            var del_pd = {"novels_name": novels_name, "chapter_url": chapter_url};
            $.ajax({
                type: "post",
                contentType: "application/json",
                url: "/operate/delete_book",
                data: del_pd,
                dataType: 'json',
                success: function (data) {
                    if (data.status == 1) {
                        $('#owllook_book').removeClass('add-color');
                    }
                    if (data.status == -1) {
                        alert('You should login');
                    }
                }
            });
        } else {
            // add book
            last_read_url = window.location.pathname + window.location.search;
            var add_pd = {"novels_name": novels_name, "chapter_url": chapter_url, 'last_read_url': last_read_url};
            $.ajax({
                type: "post",
                contentType: "application/json",
                url: "/operate/add_bookshelf",
                data: add_pd,
                dataType: 'json',
                success: function (data) {
                    if (data.status == 1) {
                        $('#owllook_book').addClass('add-color');
                        alert('^_^ You have add this page into your bookshelf');
                        window.location.reload();

                    }
                    if (data.status == -1) {
                        alert('Please login');
                    }
                }
            });
        }
    });

    // bookmark
    $('#bookMark').click(function () {
        var chapter_url = $("#chapter_url").val();
        var novels_name = $("#novels_name").val();
        var url = $("#url").val();
        var content_name = $("#content_name").text();
        bookmarkurl = "/quickreading_content?url=" + url + "&name=" + content_name + "&chapter_url=" + chapter_url + "&novels_name=" + novels_name;
        if ($(this).hasClass('bookMark')) {
            // add bookmark
            var add_bm_pd = {'bookmark_url': bookmarkurl};
            $.ajax({
                type: "post",
                contentType: "application/json",
                url: "/operate/add_bookmark",
                data: add_bm_pd,
                dataType: 'json',
                success: function (data) {
                    if (data.status == 1) {
                        $('#bookMark').removeClass('bookMark');
                        $('#bookMark').addClass('bookMarkAct');
                    }
                    if (data.status == -1) {
                        alert('您还没有登录');
                    }
                }
            });
        } else {
            // delete bookmark
            var del_bm_pd = {'bookmarkurl': bookmarkurl};
            $.ajax({
                type: "post",
                contentType: "application/json",
                url: "/operate/delete_bookmark",
                data: del_bm_pd,
                dataType: 'json',
                success: function (data) {
                    if (data.status == 1) {
                        $('#bookMark').removeClass('bookMarkAct');
                        $('#bookMark').addClass('bookMark');
                    }
                    if (data.status == -1) {
                        alert('您还没有登录');
                    }
                }
            });
        }
    });

    // login
    $("#owllook_login").click(function () {
        var owllook_user = $("#owllook_user").val();
        var owllook_pass = $("#owllook_pass").val();
        if (owllook_user == "" || owllook_pass == "") {
            alert('Content should not be NULL!!!');
        } else {
            var login_pd = {'user': owllook_user, 'pwd': owllook_pass};
            $.ajax({
                type: "post",
                contentType: "application/json",
                url: "/operate/login",
                data: login_pd,
                dataType: 'json',
                success: function (data) {
                    if (data.status == 1) {
                        location.reload();
                    }
                    if (data.status == -1) {
                        alert('User name wrong');
                    }
                    if (data.status == -2) {
                        alert('Password wrong');
                    }
                }
            });
        }
    });
    // logout
    $("#logout").click(function () {
        $.ajax({
            type: "get",
            contentType: "application/json",
            url: "/operate/logout",
            dataType: 'json',
            success: function (data) {
                if (data.status == 1) {
                    location.reload();
                }
            }
        });
    })
});


