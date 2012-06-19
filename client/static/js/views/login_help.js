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
    }
});

