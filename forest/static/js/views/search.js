PANDA.views.Search = Backbone.View.extend({
    el: $("#content"),

    template: PANDA.templates.search,

    query: null,

    initialize: function(options) {
        _.bindAll(this, "render");

        if (!_.isUndefined(options.query)) {
            this.query = options.query;
        }

        this.render();
        
        this.results = new PANDA.views.SearchResults({ collection: this.collection, el: $("#search-results") });

        this.results.render();
    },

    render: function() {
        this.el.html(this.template({ query: this.query }));
    }
});

