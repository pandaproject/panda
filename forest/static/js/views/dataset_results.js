PANDA.views.DatasetResults = Backbone.View.extend({
    template: PANDA.templates.dataset_results,

    events: {
        "click a.prev": "scroll_to_top",
        "click a.next": "scroll_to_top"
    },

    dataset: null,

    initialize: function(options) {
        _.bindAll(this, "render");

        search = options.search;
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
        this.dataset.data.bind("reset", this.render);
    },

    render: function() {
        results = this.dataset.results();
        results['query'] = search.query;
        console.log(results);
        this.el.html(this.template(results));
    },

    scroll_to_top: function() {
        window.scrollTo(0, this.el.offset());
    }
});
