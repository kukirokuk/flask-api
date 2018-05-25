$("button").click(function(){
    var set_key = $("#set-key").val()
    var set_value = $("#set-value").val()
    $.ajax({
        type: 'POST',
        url: '/set/',
        data: JSON.stringify({"key": set_key, "value": set_value}),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data) {
            console.log(data);
            $("#message").html("<ul>"+data.value+"</ul>");
        },
        failure: function(errMsg){
            alert(errMsg);
        }
    });
});