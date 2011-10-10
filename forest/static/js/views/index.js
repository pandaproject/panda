Redd.views.Index = Backbone.View.extend({
    el: $("#content"),
    
    template: JST.index,

    initialize: function() {
        _.bindAll(this, 'render');

        this.render();
    },

    render: function() {
        console.log('rendering');
        console.log(this.el);
        this.el.html(this.template());
    }
});

