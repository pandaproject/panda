PANDA.views.Login = Backbone.View.extend({
    el: $("#content"),
    
    events: {
        "submit #login-form":   "login"
    },

    next: null,

    initialize: function() {
        _.bindAll(this, "render");
    },

    reset: function(next) {
        this.next = next;

        // Ensure the sidebar is hidden
        // Normally this happens during authentication, but if the loser
        // moves to the login page from an unathenticated page that
        // may never happen.
        $("#sidebar").hide();

        this.render();
    },

    render: function() {
        var email = $.cookie("email");

        this.el.html(PANDA.templates.login({ email: email }));
    },

    validate: function() {
        var data = $("#login-form").serializeObject();
        var errors = {};

        if (!data["email"]) {
            errors["email"] = ["Please enter your email."];
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
            success: _.bind(function(data, status, xhr) {
                Redd.set_current_user(new PANDA.models.User(data));

                if (!_.isUndefined(this.next) && !_.isNull(this.next)) {
                    window.location.hash = this.next;
                } else {
                    Redd.goto_search();
                }
            }, this),
            error: function(xhr, status, error) {
                Redd.set_current_user(null); 

                try {
                    var errors = $.parseJSON(xhr.responseText);
                } catch(e) {
                    var errors = { "__all__": "Unknown error" }; 
                }

                $("#login-form").show_errors(errors, "Login failed!");
            }
        });

        return false;
    }
});


