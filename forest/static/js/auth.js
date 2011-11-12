(function() {
    /*
     * Override the Backbone sync handler to attach authorization headers
     * and handle failures.
     */
    var Backbone = this.Backbone;

    Backbone.noAuthSync = Backbone.sync;

    Backbone.sync = function(method, model, options) {
        var dfd = new $.Deferred();

        check_auth_cookies();

        // Handle authentication failures
        dfd.fail(function(xhr, status, error) {
            if (xhr.status == 401) {
                window.location = "#login";
            }
        });

        // Trigger original error handler after checking for auth issues
        dfd.fail(options.error);
        options.error = dfd.reject;

        dfd.request = Backbone.noAuthSync(method, model, options);

        return dfd;
    }
})();

$.panda_ajax = function(options) {
    /*
     * Attach authorization headers and handle failures.
     */
    var dfd = new $.Deferred();
    
    check_auth_cookies();

    // Handle authentication failures
    dfd.fail(function(responseXhr, status, error) {
        if (responseXhr.status == 401) {
            window.location = "#login";
        }
    });

    // Trigger original error handler after checking for auth issues
    dfd.fail(options.error);
    options.error = dfd.reject;

    dfd.request = $.ajax(options);

    return dfd;
}

window.check_auth_cookies = function() {
    /* 
     * Check cookies for headers, if they don't exist redirect to login.
     */
    console.log("here");
    username = $.cookie("username");
    api_key = $.cookie("api_key");

    if (username === null || api_key === null) {
        window.location = "#login";
        return false;
    }

    return true;
}
        
