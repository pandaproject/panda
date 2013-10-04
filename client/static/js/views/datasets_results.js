PANDA.views.DatasetsResults = Backbone.View.extend({
    search: null,

    text: PANDA.text.DatasetsResults(),

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function(search) {
        this.search = search;
    },

    render: function() {
        var pager_context = PANDA.utils.make_context(this.search.datasets.meta);
        pager_context.text = PANDA.inlines_text;
        pager_context.pager_unit = "dataset";
        pager_context.row_count =  this.search.datasets.meta.total_count;
        
        var pager = PANDA.templates.inline_pager(pager_context);

        var context = PANDA.utils.make_context(this.search.datasets.meta);

        context["text"] = this.text;
        context["query"] = this.search.query;
        context["category"] = this.search.category;
        context["datasets"] = this.search.datasets.results()["datasets"];
        context["pager_unit"] = "dataset";
        context["row_count"] = this.search.datasets.meta.total_count;
        context["root_url"] = "#datasets/" + this.search.category + "/" + (this.search.query || "*");

        context["pager"] = pager;

        this.$el.html(PANDA.templates.datasets_results(context));

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

