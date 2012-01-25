PANDA.views.NotFound = Backbone.View.extend({
    el: $("#content"),
    
    initialize: function() {
        _.bindAll(this, "render");
    },

    reset: function(path) {
        this.render();
    },

    render: function() {
        this.el.html(PANDA.templates.not_found());
    }
});

