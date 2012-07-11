PANDA.views.User = Backbone.View.extend({
    events: {
        "click #subscriptions li .delete":  "delete_subscription",
        "click #user-edit":                 "edit",
        "click #user-change-password":      "change_password"
    },

    user: null,
    edit_view: null,
    change_password_view: null,

    initialize: function(options) {
        _.bindAll(this);
        
        this.edit_view = new PANDA.views.UserEdit();
        this.change_password_view = new PANDA.views.ChangePassword();
    },

    reset: function(id) {
        var error = false;

        this.user = new PANDA.models.User({ resource_uri: PANDA.API + "/user/" + id + "/" });

        this.user.fetch({
            async: false,
            data: {
                "notifications": true,
                "datasets": true,
                "exports": true,
                "search_subscriptions": true
            },
            error: _.bind(function(model, response) {
                error = true;

                if (response.status == 404) {
                    Redd.goto_not_found(); 
                } else {
                    Redd.goto_server_error();
                }
            }, this)
        });

        if (error) {
            return;
        }

        this.edit_view.set_user(this.user);
        this.change_password_view.set_user(this.user);

        this.render();
    },

    render: function() {
        var context = PANDA.utils.make_context({
            user: this.user.toJSON(true),
            current_user: Redd.get_current_user().toJSON() 
        });

        this.$el.html(PANDA.templates.user(context));

        this.edit_view.setElement("#modal-edit-user");
        
        this.change_password_view.setElement("#modal-user-change-password");

        $('#modal-edit-user').on('shown', function () {
            $("#user-first-name").focus();
        });

        $('#modal-user-change-password').on('shown', function () {
            $("#user-current-password").focus();
        });
    },

    edit: function() {
        this.edit_view.render();
        $("#modal-edit-user").modal("show");
    },

    change_password: function() {
        this.change_password_view.render();
        $("#modal-user-change-password").modal("show");
    },

    delete_subscription: function(e) {
        var element = $(e.currentTarget);
        var uri = element.attr("data-uri"); 
        var sub = this.user.subscriptions.get(uri);

        bootbox.dialog(
            "Are you sure you want to delete this subscription?",
            [
                {
                    "label": "Delete",
                    "class": "btn-danger",
                    "callback": _.bind(function(result) {
                        this.user.subscriptions.remove(sub);
                        sub.destroy();
                        element.parent("li").remove();
                    }, this)
                },
                {
                    "label": "Cancel"
                }
            ]
        );
    }
});

