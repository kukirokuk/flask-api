
$("#get-value").click(function(){
    var $value = $('#value');

    $.ajax({
        type: 'GET',
        url: '/get/' + $("#key").val(),
        success: function(data) {
            console.log('success', data);
            $value.html("<ul>"+data.value+"</ul>");
        }
    });
});

