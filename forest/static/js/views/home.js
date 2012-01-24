PANDA.views.Home = Backbone.View.extend({
    template: PANDA.templates.home,

    initialize: function(options) {
        _.bindAll(this, "render");
    },

    render: function() {
        var recent_datasets = new PANDA.collections.Datasets()
        recent_datasets.fetch({ data: { limit: 5 }, success: _.bind(function() {
            this.el.html(this.template({
                recent: recent_datasets.results()
            }));
        }, this) });
    }
});

