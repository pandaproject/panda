PANDA.views.DatasetsSearch = Backbone.View.extend({
    el: $("#content"),

    events: {
        "submit #datasets-search-form":      "search_event"
    },

    category: null,
    datasets: null,
    query: null,

    initialize: function(options) {
        _.bindAll(this);

        this.datasets = new PANDA.collections.Datasets();
        this.results = new PANDA.views.DatasetsResults({ search: this });
    },

    reset: function(category, query, limit, page) {
        this.category = category;
        this.query = query;

        this.render();

        // Bypass search if there are no query terms
        if (category == "all" && !query) {
            this.datasets.search_meta(null, query, limit, page);
        } else if (category != "all") {
            this.datasets.search_meta(category, query, limit, page);
        } else {
            this.datasets.search_meta(null, query, limit, page);
        }
    },

    render: function() {
        var context = PANDA.utils.make_context({
            categories: Redd.get_categories(),
            category: this.category,
            query: this.query,
            datasets: this.datasets.results()
        });

        this.el.html(PANDA.templates.datasets_search(context));

        this.results.el = $("#datasets-search-results");

        $('a[rel="popover"]').popover();
    },

    search_event: function() {
        this.category = $("#datasets-search-form #datasets-search-category").val();
        this.query = $("#datasets-search-form #datasets-search-query").val();

        Redd.goto_datasets_search(this.category, this.query);

        return false;
    }
});

