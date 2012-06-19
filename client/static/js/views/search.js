PANDA.views.Search = Backbone.View.extend({
    el: $("#content"),

    events: {
        "submit #search-form":      "search_event"
    },

    datasets:  new PANDA.collections.Datasets(),
    query: null,
    category: null,
    since: "all",
    results: null,
    home_view: null,

    initialize: function() {
        _.bindAll(this);

        this.results = new PANDA.views.SearchResults({ datasets: this.datasets, search: this });
        this.home_view = new PANDA.views.Home();
    },

    reset: function(category, query) {
        this.query = query;
        this.category = category;
        this.since = "all";
        this.render();
    },

    render: function() {
        var context = PANDA.utils.make_context({
            categories: Redd.get_categories(),
            category: this.category,
            query: this.query
        });

        this.el.html(PANDA.templates.search(context));

        this.results.el = $("#search-results");
        this.home_view.el = $("#search-results");

        if (!this.query) {
            this.home_view.render();
        }

        $('a[rel="popover"]').popover();
    },

    search_event: function() {
        this.category = $("#search-form #search-category").val();
        this.query = $("#search-form #search-query").val();

        Redd.goto_search(this.category, this.query);

        return false;
    },

    search: function(category, query, since, limit, page) {
        /*
         * Execute cross-dataset search.
         *
         * TODO: error handler
         */
        this.query = query;
        this.category = category;
        this.since = since || "all";

        this.render();

        if (this.query) {
            this.datasets.search(
                category,
                query,
                since,
                limit,
                page,
                _.bind(function(datasets) {
                    this.results.render(); 
                }, this)
            );
        } else {
            this.render();
        }
    }
});

