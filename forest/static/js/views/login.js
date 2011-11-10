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

    validate: function() {
        var data = $("#login-form").serializeObject();
        var errors = {};

        if (!data["username"]) {
            errors["username"] = ["Please enter your username."];
        }

        if (!data["password"]) {
            errors["password"] = ["Please enter your password."];
        }

        return errors;
    },

    login: function() {
        var errors = this.validate();

        if (!_.isEmpty(errors)) {
            $("#login-form").show_errors(errors, "Login failed!");
        
            return false;
        }

        $.ajax({
            url: '/login/',
            dataType: 'json',
            type: 'POST',
            data: $("#login-form").serialize(),
            success: function(data, status, xhr) {
                $.cookie('username', data.username);
                $.cookie('api_key', data.api_key);

                Redd.configure_topbar();

                window.location = "#";
            },
            error: function(xhr, status, error) {
                $.cookie('username', null);
                $.cookie('api_key', null);
                
                Redd.configure_topbar();

                try {
                    errors = $.parseJSON(xhr.responseText);
                } catch(e) {
                    errors = { "__all__": "Unknown error" }; 
                }

                $("#login-form").show_errors(errors, "Login failed!");
            }
        });

        return false;
    },
});


