PANDA.views.DatasetsSearch = Backbone.View.extend({
    el: $("#content"),

    template: PANDA.templates.datasets_search,

    events: {
        "submit #datasets-search-form":      "search_event"
    },

    category: null,
    datasets: null,
    query: null,

    initialize: function(options) {
        _.bindAll(this, "render");

        this.datasets = new PANDA.collections.Datasets();
        this.results = new PANDA.views.DatasetsResults({ search: this });
    },

    reset: function(category, query, limit, page) {
        this.category = category;
        this.query = query;

        this.render();

        // Bypass search if there are no query terms
        if (!category && !query) {
            this.datasets.search_meta(null, query, 10, 1);
        } else if (category) {
            this.datasets.search_meta(Redd.get_category_by_slug(category).get("id"), query, null, null);
        } else {
            this.datasets.search_meta(null, query, null, 1);
        }
    },

    render: function() {
        categories = Redd.get_categories();

        this.el.html(this.template({
            categories: categories,
            category: this.category,
            query: this.query,
            datasets: this.datasets.results()
        }));

        this.results.el = $("#datasets-search-results");
    },

    search_event: function() {
        this.category = $("#datasets-search-form #datasets-search-category").val();
        this.query = $("#datasets-search-form #datasets-search-query").val();

        Redd.goto_datasets_search(this.category, this.query);

        return false;
    }
});

