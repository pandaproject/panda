PANDA.views.ChangePassword = Backbone.View.extend({
    events: {
        "click #user-change-password-save":   "change_password_save"
    },

    user: null,

    text: PANDA.text.ChangePassword(),

    initialize: function(options) {
        _.bindAll(this);
    },

    set_user: function(user) {
        this.user = user;
    },

    render: function() {
        var context = PANDA.utils.make_context({
            text: this.text,
            user: this.user.toJSON(true)
        });

        this.$el.html(PANDA.templates.modal_change_password(context));
        
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

        if (!data["current-password"]) {
            errors["current-password"] = [gettext("This field is required.")];
        } else {
            $.ajax({
                url: '/login/',
                dataType: 'json',
                type: 'POST',
                data: { email: Redd.get_current_user().get("email"), password: data["current-password"] },
                async: false,
                error: function(xhr, status, error) {
                    errors["current-password"] = [gettext("Incorrect password.")]; 
                }
            });
        }

        if (!data["password"]) {
            errors["password"] = [gettext("This field is required.")];
        }

        if (!data["password2"]) {
            errors["password2"] = [gettext("Reenter your password.")];
        }

        if (data["password"] != data["password2"]) {
            errors["password2"] = [gettext("Passwords do not match.")];
        }

        return errors;
    },

    change_password_save: function() {
        /*
         * Update user's password.
         */
        var errors = this.validate();

        if (!_.isEmpty(errors)) {
            $("#user-change-password-form").show_errors(errors, gettext("Save failed!"));
        
            return false;
        }
        
        var form_values = $("#user-change-password-form").serializeObject();

        this.user.patch(
            form_values,
            _.bind(function(response) {
                $("#modal-user-change-password").modal("hide");
            }, this),
            function(model, response) {
                try {
                    errors = $.parseJSON(response);
                } catch(e) {
                    errors = { "__all__": gettext("Unknown error") }; 
                }

                $("#user-change-password-form").show_errors(errors, gettext("Save failed!"));
            }
        );

        return false;
    }
})

