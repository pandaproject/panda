(function() {
    var Backbone = this.Backbone;

    Backbone.noAuthSync = Backbone.sync;

    Backbone.sync = function(method, model, options) {
        //var dfd = new $.Deferred();
        //dfd.done();
        
        auth_headers = $.get_auth_headers();

        options.headers = options.headers || {};
        options.headers = _.extend(options.headers, auth_headers);

        // TODO - handle auth errors
        
        /*$.ajax({
            url: '/api_key/',
            dataType: 'json',
            success: function(data, status, xhr) {
                options.data = _.extend(options.data, { username: data.username, api_key: data.api_key });
                dfd.resolveWith(options.context, [method, model, options]);
            },
            error: function(xhr, status, error) {
                if (xhr.status == 401) {
                    window.location = '#login';
                    dfd.reject();
                }
            }
        });*/

        // return dfd;
        return Backbone.noAuthSync(method, model, options);
    }
})();

$.get_auth_headers = function() {
    username = $.cookie("username");
    api_key = $.cookie("api_key");

    if (username == null || api_key == null) {
        window.location = "#login";
    }

    return { 'PANDA_USERNAME': username, 'PANDA_API_KEY': api_key };
}
        
