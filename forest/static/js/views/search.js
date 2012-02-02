PANDA.views.Search = Backbone.View.extend({
    el: $("#content"),

    events: {
        "submit #search-form":      "search_event"
    },

    collection:  new PANDA.collections.Datasets(),
    query: null,
    home_view: null,

    initialize: function() {
        _.bindAll(this);

        this.results = new PANDA.views.SearchResults({ collection: this.collection, search: this });
        this.home_view = new PANDA.views.Home();
    },

    reset: function(query) {
        this.query = query;
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

    search: function(query, limit, page) {
        this.query = query;

        if (this.query) {
            this.collection.search(query, limit, page);
        } else {
            this.render();
        }
    }
});

