PANDA.views.Search = Backbone.View.extend({
    el: $("#content"),

    events: {
        "submit #search-form":      "search_event"
    },

    datasets:  new PANDA.collections.Datasets(),
    query: null,
    since: "all",
    results: null,
    home_view: null,

    initialize: function() {
        _.bindAll(this);

        this.results = new PANDA.views.SearchResults({ datasets: this.datasets, search: this });
        this.home_view = new PANDA.views.Home();
    },

    reset: function(query) {
        this.query = query;
        this.since = "all";
        this.render();
    },

    render: function() {
        var context = PANDA.utils.make_context({ query: this.query });

        this.el.html(PANDA.templates.search(context));

        this.results.el = $("#search-results");
        this.home_view.el = $("#search-results");

        if (!this.query) {
            this.home_view.render();
        }

        $('a[rel="popover"]').popover();
    },

    search_event: function() {
        this.query = $("#search-form #search-query").val();

        Redd.goto_search(this.query);

        return false;
    },

    search: function(query, since, limit, page) {
        /*
         * Execute cross-dataset search.
         *
         * TODO: error handler
         */
        this.query = query;
        this.since = since || "all";

        if (this.query) {
            this.datasets.search(
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

