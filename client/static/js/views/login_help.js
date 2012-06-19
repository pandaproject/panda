PANDA.views.LoginHelp = Backbone.View.extend({
    el: $("#content"),

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function() {
        this.render();
    },

    render: function() {
        var context = PANDA.utils.make_context({});

        this.el.html(PANDA.templates.login_help(context));

        $("#show-again").click(this.show_again);
        $("#dont-show-again").click(this.dont_show_again);
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

