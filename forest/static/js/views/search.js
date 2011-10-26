PANDA.views.Search = Backbone.View.extend({
    el: $("#content"),

    template: PANDA.templates.search,

    events: {
        "submit #search-form":      "search"
    },

    query: null,

    initialize: function(options) {
        _.bindAll(this, "render");

        this.results = new PANDA.views.SearchResults({ collection: this.collection });
    },

    reset: function(query) {
        this.query = query;
        this.render();
        this.collection.reset();
    },

    render: function() {
        this.el.html(this.template({ query: this.query }));
        this.results.el = $("#search-results");
    },

    search: function() {
        query = $("#search-form #search-query").val();

        window.location = "#search/" + query;

        return false;
    }
});

