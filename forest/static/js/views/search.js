PANDA.views.Search = Backbone.View.extend({
    el: $("#search-wrapper"),

    events: {
        "submit #search-form": "search"
    },

    initialize: function() {
        _.bindAll(this, "render");
        
        this.results = new PANDA.views.SearchResults({ collection: this.collection, el: $("#content") });
    },

    search: function() {

        this.collection.search($("#search-form #search-query").val(), 10, 0);
        return false;
    },
});

