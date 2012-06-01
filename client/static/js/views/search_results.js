PANDA.views.SearchResults = Backbone.View.extend({
    datasets: null,
    search: null,

    initialize: function(options) {
        _.bindAll(this);

        this.datasets = options.datasets; 
        this.search = options.search;
    },

    render: function() {
        // Nuke old modals
        $("#modal-export-search-results").remove();
        $("#modal-subscribe-search-results").remove();

        var context = PANDA.utils.make_context(this.datasets.meta);

        context["query"] = this.search.query,
        context["root_url"] = "#search/" + this.search.query + "/" + this.search.since;
        context["pager_unit"] = "dataset";
        context["row_count"] = null;
        context["datasets"] = this.datasets.results();

        context["pager"] = PANDA.templates.inline_pager(context);

        this.el.html(PANDA.templates.search_results(context));

        $("#search-results-export").click(this.export_results);
        $("#search-results-subscribe").click(this.subscribe_results);
    },
    
    subscribe_results: function() {
        /*
         * Subscribe to search results.
         */
        sub = new PANDA.models.SearchSubscription({
            dataset: null,
            query: this.search.query
        });

        sub.save({}, {
            async: false,
            success: _.bind(function(model, response) {
                bootbox.alert("You are now subscribed to notifications for this query.");
            }, this),
            error: function(model, response) {
                error = JSON.parse(response);
                bootbox.alert("<p>Failed to subscribe to notifications!</p><p>Error:</p><code>" + error.traceback + "</code>");
            }
        });
    }
});

