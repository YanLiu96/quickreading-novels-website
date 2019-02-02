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
// login
    $("#owllook_login").click(function () {
        var owllook_user = $("#owllook_user").val();
        var owllook_pass = $("#owllook_pass").val();
        if (owllook_user == "" || owllook_pass == "") {
            alert('不能有内容为空');
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
                        alert('用户名错误');
                    }
                    if (data.status == -2) {
                        alert('密码错误');
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

$('.we-button').popover({
    trigger: 'hover',
    html: true,
    content: "<img width='120px' height='120px' src='static/novels/img/lcxs.jpg'><p style='text-align: center'><span>关注后回复进群</span></p>"
});

$('.lcxs-button').popover({
    trigger: 'hover',
    html: true,
    content: "<img width='120px' height='120px' src='static/novels/img/lcxs.jpg'><p style='text-align: center'><span>微信关注粮草小说</span></p>"
});

