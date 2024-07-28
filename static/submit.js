console.log('submit.js loaded');
function initApiCall(data, credentials) {
    console.log('Initiating API call...');
    console.log(data);
    console.log(credentials);
    $.ajax({
        type: 'POST',
        url: 'https://api.braspress.com/v1/cotacao/calcular/json',
        data: data,
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        xhrFields: {
        withCredentials: true
        },
        crossDomain: true,
        headers: {
        'Authorization': 'Basic ' + credentials,
        },
        success: function (result) {
            console.log('API call successful.');
            // Send the result to the Flask app and set the values of the hidden form fields
            var resultString = JSON.stringify(result);
            var dataString = data;
            window.location.href = "/api/response?var1=" + resultString + "&var2=" + dataString;
        },
        error: function (req, status, error) {
            console.log(req);
            console.log(status);
            console.log(error);
            if (req.responseJSON) {
                console.log("Error statusCode:", req.responseJSON.statusCode);
                console.log("Error message:", req.responseJSON.message);
                console.log("Error dateTime:", req.responseJSON.dateTime);
        
                // Check if errorList exists and is an array
                if (Array.isArray(req.responseJSON.errorList)) {
                    console.log("Error list:");
                    req.responseJSON.errorList.forEach(function(error, index) {
                        console.log(`Error ${index + 1}:`, error);
                    });
                }
            } else {
                // Fallback if responseJSON is not available
                console.log("Error:", req.responseText);
            }
            // Send the error details to the Flask app
            $.ajax({
                type: 'POST',
                url: '/api/error', // Flask route for handling errors
                data: JSON.stringify({status: req.status, statusText: req.statusText, responseText: req.responseText}),
                contentType: 'application/json; charset=utf-8',
                success: function () {
                    console.log('Error data sent to Flask app successfully.');
                },
                error: function () {
                    console.log('Failed to send error data to Flask app.');
                }
            });
        }
    });
}