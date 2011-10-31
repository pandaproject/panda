PANDA.views.DatasetResults = Backbone.View.extend({
    template: PANDA.templates.dataset_results,

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
        context = {
            dataset: this.dataset.results(),
            query: search.query
        }

        this.el.html(this.template(context));

        $("a.prev, a.next").click(this.scroll_to_top);
    },

    scroll_to_top: function() {
        window.scrollTo(0, 0);
    }
});
