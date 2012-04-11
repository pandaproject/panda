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
        if (category == "all") {
            category = null;
        }

        this.category = category;
        this.query = query;

        this.render();

        // Bypass search if there are no query terms
        if (!category && !query) {
            this.datasets.search_meta(null, query, 10, 1);
        } else if (category) {
            this.datasets.search_meta(category, query, null, null);
        } else {
            this.datasets.search_meta(null, query, null, 1);
        }
    },

    render: function() {
        var categories = Redd.get_categories();

        var context = PANDA.utils.make_context({
            categories: categories,
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

