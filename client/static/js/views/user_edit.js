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

        this.el.html(PANDA.templates.modal_user_edit(context));

        $("#user-edit-save").click(this.edit_save);
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

        this.user.patch(s, 
            _.bind(function(response) {
                $("#modal-edit-user").modal("hide");
                Redd.goto_user_view(this.user.get("id"));
            }, this),
            function(model, response) {
                try {
                    errors = $.parseJSON(response);
                } catch(e) {
                    errors = { "__all__": "Unknown error" }; 
                }

                $("#edit-user-form").show_errors(errors, "Save failed!");
            });

        return false;
    }
})

