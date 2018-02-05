function createButtonPressed() {
    var appName = $("#app-name").val();

    var appData = {};
    appData['name'] = appName;

    $.ajax({
        type: "POST",
        contentType: 'application/json',
        dataType: "json",
        url: "/operation/new/app",
        data: JSON.stringify(appData),
        success: function (result) {
            window.location = '/app';
        },
        error: function (error) {
            if (error.status === 500) {
                //TODO: Display error
            }
        }
    });
}