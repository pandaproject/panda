PANDA.views.Notifications = Backbone.View.extend({
    el: $("#content"),

    notifications: null,

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function(limit, page) {
        this.notifications = new PANDA.collections.Notifications();

        this.notifications.fetch({
            async: false
        });

        this.render();
    },

    render: function() {
        var context = PANDA.utils.make_context({
            notifications: this.notifications.toJSON(true)
        });

        this.el.html(PANDA.templates.notifications(context));
    }
});

