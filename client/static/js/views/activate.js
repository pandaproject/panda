PANDA.views.Activate = Backbone.View.extend({
    events: {
        "submit #activation-form":   "activate"
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

                $("#activation-form").show_errors(errors, "Activation failed!");
            }, this)
        });
    },

    render: function(data) {
        var context = PANDA.utils.make_context(data)
        this.$el.html(PANDA.templates.activate(context));
    },

    validate: function() {
        var data = $("#activation-form").serializeObject();
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

    activate: function() {
        var errors = this.validate();

        if (!_.isEmpty(errors)) {
            $("#activation-form").show_errors(errors, "Activation failed!");

            return false;
        }

        $.ajax({
            url: '/activate/',
            dataType: 'json',
            type: 'POST',
            data: $("#activation-form").serialize(),
            success: function(data, status, xhr) {
                Redd.set_current_user(new PANDA.models.User(data));
                
                if (data.show_login_help) {
                    Redd.goto_welcome();
                } else {
                    Redd.goto_search("all");
                }
            },
            error: function(xhr, status, error) {
                Redd.set_current_user(null);

                try {
                    errors = $.parseJSON(xhr.responseText);
                } catch(e) {
                    errors = { "__all__": "Unknown error" }; 
                }

                $("#activation-form").show_errors(errors, "Activation failed!");
            }
        });

        return false;
    }
});


