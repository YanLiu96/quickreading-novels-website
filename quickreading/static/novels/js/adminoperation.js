$(document).ready(function () {
    $(".delete-user").click(function () {
        var msg = "Are you sure to delete this user?";
        if (confirm(msg)) {
            var user_name = $(this).find('a.delete-user').attr("data-value");
            var del_pd = {"user_name": user_name};
            var del_object = $(this).parent();
            $.ajax({
                type: "post",
                contentType: "application/json",
                url: "/operate/delete_user",
                data: del_pd,
                dataType: 'json',
                success: function (data) {
                    if (data.status == 1) {
                        del_object.remove();
                    }
                    if (data.status == -1) {
                        alert('Sorry, you do not delete it');
                    }
                }
            });
        }
    });
});