PANDA.views.NotFound = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.not_found,

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

