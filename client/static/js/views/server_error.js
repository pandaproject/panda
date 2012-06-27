PANDA.views.ServerError = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this);
    },

    reset: function(path) {
        this.render();
    },

    render: function() {
        this.$el.html(PANDA.templates.server_error());
    }
});

