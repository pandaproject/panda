PANDA.views.Notifications = Backbone.View.extend({
    notifications: null,

    text: PANDA.text.Notifications(),

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function(limit, page) {
        this.notifications = new PANDA.collections.Notifications();

        this.notifications.fetch({
            async: false,
            data: {
                limit: limit || 10,
                offset: ((page - 1) * limit) || 0
            }
        });

        this.render();
    },

    render: function() {
        var context = PANDA.utils.make_context(this.notifications.meta);
            
        _.extend(context, {
            text: this.text,
            notifications: this.notifications.toJSON(),
            root_url: "#notifications",
            pager_unit: "notification",
            row_count: this.notifications.length
        });

        context["pager"] = PANDA.templates.inline_pager(context);

        this.$el.html(PANDA.templates.notifications(context));
    }
});

