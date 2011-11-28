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
        this.datasets.search_meta(category, query, limit, page);
    },

    render: function() {
        this.el.html(this.template({ query: this.query, datasets: this.datasets.results() }));
        this.results.el = $("#datasets-search-results");
    },

    search_event: function() {
        this.query = $("#datasets-search-form #datasets-search-query").val();

        Redd.goto_datasets_search(this.category, this.query);

        return false;
    }
});

