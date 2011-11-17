PANDA.views.ServerError = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.server_error,

    initialize: function() {
        _.bindAll(this, "render");
    },

    reset: function(path) {
        this.render();
    },

    render: function() {
        this.el.html(this.template());
    }
});

