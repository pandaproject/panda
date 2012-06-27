PANDA.views.DatasetsSearch = Backbone.View.extend({
    events: {
        "submit #datasets-search-form":      "search_event"
    },

    category: null,
    datasets: null,
    query: null,

    initialize: function(options) {
        _.bindAll(this);

        this.datasets = new PANDA.collections.Datasets();
        this.results = new PANDA.views.DatasetsResults();
    },

    reset: function(category, query, limit, page) {
        /*
         * Execute the search.
         *
         * TODO: error handler
         */
        this.category = category;
        this.query = query;

        this.render();
        
        this.datasets.search_meta(
            (this.category == "all") ? null : this.category,
            this.query,
            limit,
            page,
            _.bind(function(datasets) {
                this.results.reset(this);
                this.results.render();
            }, this)
        );
    },

    render: function() {
        var context = PANDA.utils.make_context({
            categories: Redd.get_categories(),
            category: this.category,
            query: this.query,
            datasets: this.datasets.results()
        });

        this.$el.html(PANDA.templates.datasets_search(context));

        this.results.setElement("#datasets-search-results");

        $('a[rel="popover"]').popover();
    },

    search_event: function() {
        this.category = $("#datasets-search-form #datasets-search-category").val();
        this.query = $("#datasets-search-form #datasets-search-query").val();

        Redd.goto_datasets_search(this.category, this.query);

        return false;
    }
});

