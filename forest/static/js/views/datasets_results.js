PANDA.views.DatasetsResults = Backbone.View.extend({
    template: PANDA.templates.datasets_results,
    pager_template: PANDA.templates.pager,

    initialize: function(options) {
        _.bindAll(this, "render");

        this.search = options.search;
        this.search.datasets.bind("reset", this.render);
    },

    render: function() {
        console.log(this);
        context = this.search.datasets.meta;
        context["settings"] = PANDA.settings;

        context["query"] = this.search.query;
        context["category"] = this.search.category;
        context["root_url"] = "#datasets";

        context["pager"] = this.pager_template(context);
        context["datasets"] = this.search.datasets.results()["datasets"];

        context["dataset_template"] = this.dataset_template;

        this.el.html(this.template(context));
    }
});


