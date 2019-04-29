$(document).ready(function () {
    $(".del-book").click(function () {
        var msg = "You really want to delete this one?";
        if (confirm(msg)) {
            var book_url = $(this).find('a.book_url').attr("data-value");
            var del_pd = {"book_url": book_url};
            var del_object = $(this).parent();
            $.ajax({
                type: "post",
                contentType: "application/json",
                url: "/operate/delete_book",
                data: del_pd,
                dataType: 'json',
                success: function (data) {
                    if (data.status == 1) {
                        del_object.remove();
                    }
                    if (data.status == -1) {
                        alert('You should login');
                    }
                }
            });
        }
    });
});