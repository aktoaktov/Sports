$("#comments").submit(function (e) {

    e.preventDefault()

    var form = $(this);
    var actionUrl = form.attr('action');

    $.ajax({
        type: "POST",
        url: actionUrl,
        data: form.serialize(),
        success: (d) => {
        }
    });

});