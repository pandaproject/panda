PANDA.views.Index = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.index,

    initialize: function() {
        _.bindAll(this, 'render');

        this.render();
    },

    render: function() {
        this.el.html(this.template());
    }
});

