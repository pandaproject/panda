PANDA.views.Activate = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.activate,

    events: {
        "submit #activation-form":   "activate"
    },

    activation_key: null,

    initialize: function() {
        _.bindAll(this, "render");
    },

    reset: function(activation_key) {
        this.activation_key = activation_key;
        this.render();
    },

    render: function() {
        this.el.html(this.template({ key: this.activation_key }));
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
                Redd.goto_search();
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


