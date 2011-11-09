PANDA.views.Login = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.login,

    events: {
        "submit #login-form":   "login"
    },

    initialize: function() {
        _.bindAll(this, "render");
    },

    reset: function() {
        this.render();
    },

    render: function() {
        username = $.cookie("username");

        this.el.html(this.template({ username: username }));
    },

    login: function() {
        $.ajax({
            url: '/login/',
            dataType: 'json',
            type: 'POST',
            data: $("#login-form").serialize(),
            success: function(data, status, xhr) {
                $.cookie('username', data.username);
                $.cookie('api_key', data.api_key);

                window.location = "#";
            },
            error: function(xhr, status, error) {
                $.cookie('username', null);
                $.cookie('api_key', null);

                try {
                    data = $.parseJSON(xhr.responseText);
                    message = data["message"];
                } catch(e) {
                    message = "Unknown error"; 
                }

                $("#login-alert").alert("error block-message", "<p><strong>Login failed!</strong> " + message + ".");
            }
        });

        return false;
    },
});


