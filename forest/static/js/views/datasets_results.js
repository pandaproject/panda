PANDA.views.DatasetsResults = Backbone.View.extend({
    template: PANDA.templates.datasets_results,
    pager_template: PANDA.templates.pager,

    initialize: function(options) {
        _.bindAll(this, "render");

        this.search = options.search;
        this.search.datasets.bind("reset", this.render);
    },

    render: function() {
        context = this.search.datasets.meta;
        context["settings"] = PANDA.settings;

        context["query"] = this.search.query;
        context["category"] = this.search.category;

        context["datasets"] = this.search.datasets.results()["datasets"];

        this.el.html(this.template(context));

        // Enable result sorting
        $("#datasets-results table").tablesorter({
            cssHeader: "no-sort-header",
            cssDesc: "sort-desc-header",
            cssAsc: "sort-asc-header",
            headers: {
                0: { sorter: "text" },
                1: { sorter: false },
                2: { sorter: "text" },
                3: { sorter: false }
            },
            textExtraction: function(node) {
                return $(node).children(".sort-value").text();
            }
        });
    }
});


