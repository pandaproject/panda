PANDA.views.Search = Backbone.View.extend({
    el: $("#content"),

    collection:  new PANDA.collections.Datasets(),

    template: PANDA.templates.search,

    events: {
        "submit #search-form":      "search_event"
    },

    query: null,

    initialize: function() {
        _.bindAll(this, "render");

        this.results = new PANDA.views.SearchResults({ collection: this.collection, search: this });
        this.news = new PANDA.views.News();
    },

    reset: function(query) {
        this.query = query;
        this.render();
    },

    render: function() {
        this.el.html(this.template({ query: this.query }));
        this.results.el = $("#search-results");
        this.news.el = $("#search-results");

        if (!this.query) {
            this.news.render();
        }
    },

    search_event: function() {
        this.query = $("#search-form #search-query").val();

        window.location = "#search/" + this.query;

        return false;
    },

    search: function(query, limit, page) {
        this.query = query;

        if (this.query) {
            this.collection.search(query, limit, page);
        } else {
            this.render();
        }
    }
});

