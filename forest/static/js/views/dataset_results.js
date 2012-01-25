PANDA.views.DatasetResults = Backbone.View.extend({
    dataset: null,

    initialize: function(options) {
        _.bindAll(this);

        this.search = options.search;
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
        this.dataset.data.bind("reset", this.render);
    },

    render: function() {
        var context = PANDA.make_context(this.dataset.data.meta);

        context["query"] = this.search.query,
        context["root_url"] = "#dataset/" + this.dataset.get("slug") + "/search/" + this.search.query;
        context["pager_unit"] = "row";
        context["row_count"] = this.dataset.get("row_count");
        context["dataset"] = this.dataset.results();

        context["pager"] = PANDA.templates.inline_pager(context);

        this.el.html(PANDA.templates.dataset_results(context));
    }
});
