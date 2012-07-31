PANDA.views.ResetPassword = Backbone.View.extend({
    events: {
        "submit #reset-form":   "reset_password"
    },

    activation_key: null,

    initialize: function() {
        _.bindAll(this);
    },

    reset: function(activation_key) {
        this.activation_key = activation_key;

        $.ajax({
            url: '/check_activation_key/' + activation_key,
            dataType: 'json',
            type: 'GET',
            success: _.bind(function(data, status, xhr) {
                data = $.parseJSON(xhr.responseText);

                this.render(data);
            }, this),
            error: _.bind(function(xhr, status, error) {
                this.render({});

                try {
                    errors = $.parseJSON(xhr.responseText);
                } catch(e) {
                    errors = { "__all__": "Unknown error" }; 
                }

                $("#reset-form").show_errors(errors, "Password reset failed!");
            }, this)
        });
    },

    render: function(data) {
        var context = PANDA.utils.make_context(data)
        this.$el.html(PANDA.templates.reset_password(context));
    },

    validate: function() {
        var data = $("#reset-form").serializeObject();
        var errors = {};

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

    reset_password: function() {
        var errors = this.validate();

        if (!_.isEmpty(errors)) {
            $("#reset-form").show_errors(errors, "Password reset failed!");

            return false;
        }

        $.ajax({
            url: '/activate/',
            dataType: 'json',
            type: 'POST',
            data: $("#reset-form").serialize(),
            success: function(data, status, xhr) {
                Redd.goto_login();
            },
            error: function(xhr, status, error) {
                Redd.set_current_user(null);

                try {
                    errors = $.parseJSON(xhr.responseText);
                } catch(e) {
                    errors = { "__all__": "Unknown error" }; 
                }

                $("#reset-form").show_errors(errors, "Password reset failed!");
            }
        });

        return false;
    }
});


