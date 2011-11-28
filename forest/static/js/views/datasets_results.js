PANDA.views.DatasetsResults = Backbone.View.extend({
    template: PANDA.templates.datasets_results,
    pager_template: PANDA.templates.pager,
    dataset_template: PANDA.templates.dataset_block,

    initialize: function(options) {
        _.bindAll(this, "render");

        this.search = options.search;
    },

    set_datasets: function(datasets) {
        this.search.datasets.data.bind("reset", this.render);
    },

    render: function() {
        context = this.datasets.meta;
        context["settings"] = PANDA.settings;

        context["query"] = this.search.query;
        context["root_url"] = "#datasets";

        context["pager"] = this.pager_template(context);
        context["datasets"] = this.datasets.results();

        context["dataset_template"] = this.dataset_template;

        this.el.html(this.template(context));
    }
});


