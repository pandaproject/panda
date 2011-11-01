PANDA.views.DatasetResults = Backbone.View.extend({
    template: PANDA.templates.dataset_results,
    pager_template: PANDA.templates.pager,
    dataset_template: PANDA.templates.dataset_block,

    dataset: null,

    initialize: function(options) {
        _.bindAll(this, "render");

        this.search = options.search;
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
        this.dataset.data.bind("reset", this.render);
    },

    render: function() {
        context = this.dataset.data.meta;
        context["settings"] = PANDA.settings;

        context["query"] = this.search.query,
        context["root_url"] = "#dataset/" + this.dataset.get("id") + "/search/" + this.search.query;

        context["pager"] = this.pager_template(context);
        context["dataset"] = this.dataset.results();
        context["dataset_block"] = this.dataset_template(context["dataset"]);

        this.el.html(this.template(context));
    }
});
