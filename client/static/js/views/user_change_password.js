PANDA.views.UserChangePassword = Backbone.View.extend({
    user: null,

    initialize: function(options) {
        _.bindAll(this);
    },

    set_user: function(user) {
        this.user = user;
    },

    render: function() {
        var context = PANDA.utils.make_context({
            'user': this.user.toJSON(true)
        });

        this.el.html(PANDA.templates.modal_user_change_password(context));

        $("#user-change-password-save").click(this.change_password_save);
        
        $("#user-change-password-form").keypress(_.bind(function(e) {
            if (e.keyCode == 13 && e.target.type != "textarea") {
                this.change_password_save(); 
            }
        }, this));
    },

    validate: function() {
        /*
         * Validate metadata for save.
         */
        var data = $("#user-change-password-form").serializeObject();
        var errors = {};

        if (!data["password"]) {
            errors["password"] = ["This field is required."];
        }

        if (!data["password2"]) {
            errors["password2"] = ["Reenter your password."];
        }

        if (data["password"] != data["password2"]) {
            errors["password2"] = ["Passwords do not match."];
        }

        return errors;
    },

    change_password_save: function() {
        /*
         * Update user's password.
         */
        var errors = this.validate();
        
        if (!_.isEmpty(errors)) {
            $("#user-change-password-form").show_errors(errors, "Save failed!");
        
            return false;
        }
        
        var form_values = $("#user-change-password-form").serializeObject();

        this.user.save(form_values, { 
            success: _.bind(function(response) {
                $("#modal-user-change-password").modal("hide");
            }, this),
            error: function(model, response) {
                try {
                    errors = $.parseJSON(response);
                } catch(e) {
                    errors = { "__all__": "Unknown error" }; 
                }

                $("#user-change-password-form").show_errors(errors, "Save failed!");
            }
        });

        return false;
    }
})

