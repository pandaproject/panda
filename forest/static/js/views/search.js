Redd.views.Search = Backbone.View.extend({
    el: $("#content"),
    
    template: JST.search,

    events: {
        "submit #search-form": "search"
    },

    initialize: function() {
        _.bindAll(this, "render");
        
        this.render();
        
        this.results = new Redd.views.SearchResults({ collection: this.collection, el: $("#search-results") });
    },

    render: function() {
        this.el.html(this.template());
    },

    search: function() {
        Data.search($("#search-form #search-query").val(), 10, 0);
        return false;
    },
});

