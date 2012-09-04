PANDA.views.UserEdit = Backbone.View.extend({
    events: {
        "click #user-edit-save":   "edit_save"
    },

    user: null,

    text: PANDA.text.UserEdit(),

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

        this.$el.html(PANDA.templates.modal_user_edit(context));

        $("#edit-user-form").keypress(_.bind(function(e) {
            if (e.keyCode == 13 && e.target.type != "textarea") {
                this.edit_save(); 
            }
        }, this));
    },

    validate: function() {
        /*
         * Validate metadata for save.
         */
        var data = $("#edit-user-form").serializeObject();
        var errors = {};

        if (!data["email"]) {
            errors["email"] = [gettext("This field is required.")];
        }

        if (!data["verify-password"]) {
            errors["verify-password"] = [gettext("This field is required.")];
        } else {
            $.ajax({
                url: '/login/',
                dataType: 'json',
                type: 'POST',
                data: { email: Redd.get_current_user().get("email"), password: data["verify-password"] },
                async: false,
                error: function(xhr, status, error) {
                    errors["verify-password"] = [gettext("Incorrect password.")]; 
                }
            });
        }

        return errors;
    },

    edit_save: function() {
        /*
         * Save metadata edited via modal.
         */
        var errors = this.validate();

        
        if (!_.isEmpty(errors)) {
            $("#edit-user-form").show_errors(errors, gettext("Save failed!"));
        
            return false;
        }
        
        var form_values = $("#edit-user-form").serializeObject();

        this.user.patch(
            form_values, 
            _.bind(function(response) {
                $("#modal-edit-user").modal("hide");
                Redd.get_current_user().set({ "email": this.user.get("email") });
                Redd.set_current_user(Redd.get_current_user());
                Redd.goto_user(this.user.get("id"));
            }, this),
            function(model, response) {
                try {
                    errors = $.parseJSON(response);
                } catch(e) {
                    errors = { "__all__": gettext("Unknown error") }; 
                }

                $("#edit-user-form").show_errors(errors, gettext("Save failed!"));
            }
        );

        $("#modal-edit-user").modal("hide");

        return false;
    }
})

