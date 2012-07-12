PANDA.views.SearchResults = Backbone.View.extend({
    events: {
        "click #search-results-export":      "export_results",
        "click #search-results-subscribe":   "subscribe_results",
    },

    search: null,

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function(search) {
        this.search = search
    },

    render: function() {
        var context = PANDA.utils.make_context(this.search.datasets.meta);

        context["query"] = this.search.query;
        context["query_human"] = "Search for <code class=\"full-text\">" + this.search.query + "</code>";

        if (this.search.category == "all") {
            context["category"] = null;
        } else {
            context["category"] = Redd.get_category_by_slug(this.search.category).toJSON();
        }

        context["since"] = this.search.since;

        if (this.search.since != "all") {
            context["all_results_url"] = "#search/" + this.search.category + "/" + this.search.query;
        }

        context["root_url"] = "#search/" + this.search.category + "/" + this.search.query + "/" + this.search.since;
        context["pager_unit"] = "dataset";
        context["row_count"] = null;
        context["datasets"] = this.search.datasets.results();

        context["pager"] = PANDA.templates.inline_pager(context);

        this.$el.html(PANDA.templates.search_results(context));
    },
    
    subscribe_results: function() {
        /*
         * Subscribe to search results.
         */
        if (this.search.category == "all") {
            category = null;
        } else {
            category = Redd.get_category_by_slug(this.search.category).id;
        }

        sub = new PANDA.models.SearchSubscription({
            dataset: null,
            query: this.search.query,
            category: category,
            query_url: this.search.query,
            query_human: "Search for <code class=\"full-text\">" + this.search.query + "</code>"
        });

        sub.save({}, {
            async: false,
            success: _.bind(function(model, response) {
                bootbox.alert("<p>You will now receive notifications for this search.</p><p>You cancel these notifications on your user page.</p>");
            }, this),
            error: function(model, response) {
                error = JSON.parse(response);
                bootbox.alert("<p>Failed to subscribe to notifications!</p><p>Error:</p><code>" + error.traceback + "</code>");
            }
        });
    },

    export_results: function() {
        /*
         * Export all results to CSV asynchronously.
         */
        this.search.datasets.export_data(
            this.search.category,
            this.search.query,
            this.search.since,
            function() {
                var note = "Your export has been successfully queued.";

                if (PANDA.settings.EMAIL_ENABLED) {
                    note += " When it is complete you will be emailed a link to download the file."
                } else {
                    note += " Your PANDA does not have email configured, so you will need to check your Notifications list to see when it is ready to be downloaded."
                }

                bootbox.alert(note);
            },
            function(error) {
                bootbox.alert("<p>Your export failed to start!</p><p>Error:</p><code>" + error.traceback + "</code>");
            }
        );
    }
});

