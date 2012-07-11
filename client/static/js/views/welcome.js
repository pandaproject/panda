PANDA.views.Welcome = Backbone.View.extend({
    events: {
        "click #show-again":        "show_again",
        "click #dont-show-again":   "dont_show_again",
    },

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function() {
        this.render();
    },

    render: function() {
        var context = PANDA.utils.make_context({});

        this.$el.html(PANDA.templates.welcome(context));
    },

    show_again: function() {
        Redd.get_current_user().set_show_login_help(true);
        Redd.goto_search("all");
    },

    dont_show_again: function() {
        Redd.get_current_user().set_show_login_help(false);
        Redd.goto_search("all");
    }
});

