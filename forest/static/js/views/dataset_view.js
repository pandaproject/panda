PANDA.views.DatasetView = Backbone.View.extend({
    template: PANDA.templates.dataset_view,

    initialize: function(options) {
        _.bindAll(this, "render");
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
    },

    render: function() {
        this.el.html(this.template(this.dataset.results()));
    }
});

