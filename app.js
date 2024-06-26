$(document).ready(function() {
    $('#freightForm').on('submit', function(e) {
        e.preventDefault();
        var formData = {/* Collect form data as JSON */};
        $.ajax({
            type: 'POST',
            url: '/quote',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(result) {
                $('#quoteResult').html(/* Display result */);
            },
            error: function() {
                $('#quoteResult').html('Error retrieving quote.');
            }
        });
    });
});