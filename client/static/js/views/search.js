PANDA.views.Search = Backbone.View.extend({
    events: {
        "submit #search-form":      "search_event"
    },

    datasets:  null,
    query: null,
    category: null,
    since: "all",
    results: null,
    home_view: null,

    text: {
        search_all_data: gettext("Search all data"),
        all: gettext("All"),
        search_placeholder: gettext("Enter a search query"),
        search: gettext("Search")
    },

    initialize: function() {
        _.bindAll(this);

        this.datasets = new PANDA.collections.Datasets();
        this.results = new PANDA.views.SearchResults();
        this.home_view = new PANDA.views.Home();
    },

    reset: function(category, query) {
        this.query = query;
        this.category = category;
        this.since = "all";

        this.results.reset(this);

        this.render();
    },

    render: function() {
        var context = PANDA.utils.make_context({
            text: this.text,
            categories: Redd.get_categories(),
            category: this.category,
            query: this.query
        });

        this.$el.html(PANDA.templates.search(context));

        this.results.setElement("#search-results");
        this.home_view.setElement("#search-results");

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

    slow_query_warning: function() {
        /*
         * Display a warning when a query is taking a very long time to return.
         */
        this.$("#search-results").html("<strong>Warning!</strong> This query seems to be taking a very long time. It may still finish or it may have failed.");
    },

    search_error: function(error) {
        /*
         * Display a server error resulting from search.
         */
        this.$("#search-results").html("<h3>Error executing query!</h3> <p>" + error.error_message + "</p>");
    },

    search: function(category, query, since, limit, page) {
        /*
         * Execute cross-dataset search.
         */
        this.query = query;
        this.category = category;
        this.since = since || "all";

        this.render();

        if (this.query) {
            var slow_query_timer = setTimeout(this.slow_query_warning, PANDA.settings.SLOW_QUERY_TIMEOUT);

            this.datasets.search(
                category,
                query,
                since,
                limit,
                page,
                _.bind(function(datasets) {
                    clearTimeout(slow_query_timer);
                    this.results.render(); 
                }, this),
                _.bind(function(datasets, error) {
                    clearTimeout(slow_query_timer);
                    this.search_error(error);
                    
                }, this)
            );
        } else {
            this.render();
        }
    }
});

