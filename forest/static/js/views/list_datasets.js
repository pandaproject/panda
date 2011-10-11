PANDA.views.ListDatasets = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.list_datasets,

    events: {
    },

    initialize: function(options) {
        _.bindAll(this, "render");

        this.collection = new PANDA.collections.Datasets();
        this.collection.bind("reset", this.render);

        this.collection.fetch();
    },

    render: function() {
        this.el.html(this.template({ datasets: this.collection.toJSON() }));
    },
});


