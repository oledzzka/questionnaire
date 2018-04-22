/**
 * Created by oleg on 21.04.18.
 */

$(document).ready(function () {
    var pk = window.location.search.substring(1).split('=')[1];
    $.ajax({
        type: "GET",
        url: Urls['core:question_list']({pk: pk})
        }).done(function (response) {
                $("#answers").html(response);
                var form = $("#give_answer");
                if (form.length) {
                    form.submit(function (event) {
                        event.preventDefault();
                        $.ajax({
                            url: $(this).attr('action'),
                            type: $(this).attr('method'),
                            data: $(this).serialize()
                        }).done(function (response) {
                            form.html(response);
                        });
                    })
                }
        });
});