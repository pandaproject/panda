PANDA.views.User = Backbone.View.extend({
    el: $("#content"),

    user: null,
    datasets: null,

    edit_view: null,
    change_password_view: null,

    initialize: function(options) {
        _.bindAll(this);
        
        this.edit_view = new PANDA.views.UserEdit();
        this.change_password_view = new PANDA.views.UserChangePassword();
        
        $("#subscriptions li .delete").live("click", this.delete_subscription);
    },

    reset: function(id) {
        var error = false;

        this.user = new PANDA.models.User({ resource_uri: PANDA.API + "/user/" + id + "/" });

        this.user.fetch({
            async: false,
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

        this.datasets = new PANDA.collections.Datasets();

        this.datasets.fetch({
            async: false,
            data: {
                creator_email: this.user.get("email"),
                simple: true,
                limit: 1000
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

        if (this.user.get("id") == Redd.get_current_user().get("id")) {
            this.user.refresh_subscriptions();
        }

        this.render();
    },

    render: function() {
        var context = PANDA.utils.make_context({
            user: this.user.toJSON(true),
            datasets: this.datasets.results(),
            current_user: Redd.get_current_user().toJSON() 
        });

        this.el.html(PANDA.templates.user(context));

        this.edit_view.el = $("#modal-edit-user");
        $("#user-edit").click(this.edit);
        
        this.change_password_view.el = $("#modal-user-change-password");
        $("#user-change-password").click(this.change_password);

        $('#subscriptions li a[rel="tooltip"]').tooltip();
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

        this.user.subscriptions.remove(sub);
        sub.destroy();
        element.parent("li").remove();

        // Destroy tooltip popup
        $(".tooltip").remove();

        return false;
    }
});

