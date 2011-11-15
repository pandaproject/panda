PANDA.views.Register = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.register,

    events: {
        "submit #register-form":   "register"
    },

    initialize: function() {
        _.bindAll(this, "render");
    },

    reset: function() {
        this.render();
    },

    render: function() {
        this.el.html(this.template());
    },

    validate: function() {
        var data = $("#register-form").serializeObject();
        var errors = {};

        if (!data["email"]) {
            errors["email"] = ["This field is required."]
        }

        if (!data["password"]) {
            errors["password"] = ["This field is required."]
        }

        if (!data["reenter_password"]) {
            errors["reenter_password"] = ["This field is required."]
        }

        if (data["password"] != data["reenter_password"]) {
            if ("password" in errors || "reenter_password" in errors) {
                // Skip
            } else {
                errors["reenter_password"] = ["Passwords do not match."]
            }
        }

        return errors;
    },

    register: function() {
        var errors = this.validate();

        if (!_.isEmpty(errors)) {
            $("#register-form").show_errors(errors, "Registration failed!");

            return false;
        }

        $.ajax({
            url: '/register/',
            dataType: 'json',
            type: 'POST',
            data: $("#register-form").serialize(),
            success: function(data, status, xhr) {
                Redd.set_current_user(new PANDA.models.User(data));

                window.location = "#";
            },
            error: function(xhr, status, error) {
                Redd.set_current_user(null);

                try {
                    errors = $.parseJSON(xhr.responseText);
                } catch(e) {
                    errors = { "__all__": "Unknown error" }; 
                }

                $("#register-form").show_errors(errors, "Registration failed!");
            }
        });

        return false;
    },
});



