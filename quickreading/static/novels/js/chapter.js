/**
 * Created by Yan Liu on 2019.2.12.
 */
$(document).ready(function () {
    var content_url = $("#content_url").val();
    var chapter_url = $("#url").val();
    var novels_name = $("#novels_name").val();
    $(".container a").each(function () {
        var url = $(this).attr('href');
        if (typeof(url) != "undefined") {
            if (url.indexOf("quickreading") < 0) {
                var name = $(this).text();
                // 当content_url=1
                if (content_url == '1') {
                    content_url = ''
                } else if (content_url == '0') {
                    // content_url=0 need to use url
                    content_url = chapter_url;
                } else if (content_url == '-1') {
                    // content_url=-1
                    content_url = chapter_url;
                }
                show_url = "quickreading_content?url=" + content_url + url + "&name=" + name + "&chapter_url=" + chapter_url + "&novels_name=" + novels_name;
                $(this).attr('href', show_url);
                $(this).attr('target', '_blank');
            }
        }
    });
});