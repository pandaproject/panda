PANDA.views.Welcome = Backbone.View.extend({
    events: {
        "click .start":        "start"
    },

    text: PANDA.text.Welcome(),

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function() {
        this.render();
    },

    render: function() {
        var context = PANDA.utils.make_context({
            text: this.text
        });

        this.$el.html(PANDA.templates.welcome(context));
    },

    start: function() {
        var show_again = this.$(".show-again").is(":checked");

        Redd.get_current_user().set_show_login_help(show_again);
        Redd.goto_search("all");
    }
});

