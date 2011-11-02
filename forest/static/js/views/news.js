PANDA.views.News = Backbone.View.extend({
    template: PANDA.templates.news,

    initialize: function(options) {
        _.bindAll(this, "render");
    },

    render: function() {
        recent_datasets = new PANDA.collections.Datasets()
        recent_datasets.fetch()

        this.el.html(this.template({ 'recent_datasets': recent_datasets }));
    }
});

