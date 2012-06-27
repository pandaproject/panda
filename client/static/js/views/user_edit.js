PANDA.views.UserEdit = Backbone.View.extend({
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

        this.$el.html(PANDA.templates.modal_user_edit(context));

        $("#user-edit-save").click(this.edit_save);

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
            errors["email"] = ["This field is required."];
        }

        if (!data["verify-password"]) {
            errors["verify-password"] = ["This field is required."];
        } else {
            $.ajax({
                url: '/login/',
                dataType: 'json',
                type: 'POST',
                data: { email: Redd.get_current_user().get("email"), password: data["verify-password"] },
                async: false,
                error: function(xhr, status, error) {
                    errors["verify-password"] = ["Incorrect password."]; 
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
            $("#edit-user-form").show_errors(errors, "Save failed!");
        
            return false;
        }
        
        var form_values = $("#edit-user-form").serializeObject();

        this.user.save(form_values, { 
            success: _.bind(function(response) {
                $("#modal-edit-user").modal("hide");
                Redd.get_current_user().set({ "email": this.user.get("email") });
                Redd.set_current_user(Redd.get_current_user());
                Redd.goto_user(this.user.get("id"));
            }, this),
            error: function(model, response) {
                try {
                    errors = $.parseJSON(response);
                } catch(e) {
                    errors = { "__all__": "Unknown error" }; 
                }

                $("#edit-user-form").show_errors(errors, "Save failed!");
            }
        });

        return false;
    }
})

