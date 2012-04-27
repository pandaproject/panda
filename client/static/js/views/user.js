PANDA.views.User = Backbone.View.extend({
    el: $("#content"),

    user: null,
    datasets: null,

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function(id) {
        this.user = new PANDA.models.User({ resource_uri: PANDA.API + "/user/" + id + "/" });
        this.datasets = new PANDA.collections.Datasets();

        this.user.fetch({
            async: false,
            success: _.bind(function(model, response) {
                this.datasets.search_meta(
                    null,
                    this.user.get("email"),
                    1000,
                    1,
                    _.bind(function(model, response) {
                        this.render();
                    }, this),
                    _.bind(function(model, response) {
                        if (response.status == 404) {
                            Redd.goto_not_found(); 
                        } else {
                            Redd.goto_server_error();
                        }
                    }, this)
                );
            }, this),
            error: _.bind(function(model, response) {
                if (response.status == 404) {
                    Redd.goto_not_found(); 
                } else {
                    Redd.goto_server_error();
                }
            }, this)
        });
    },

    render: function() {
        var context = PANDA.utils.make_context({
            user: this.user.toJSON(),
            datasets: this.datasets.results()
        });

        this.el.html(PANDA.templates.user(context));
    }
});

