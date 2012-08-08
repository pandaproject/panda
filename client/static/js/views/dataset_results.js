PANDA.views.DatasetResults = Backbone.View.extend({
    events: {
        "click #search-results-export":      "export_results",
        "click #search-results-subscribe":   "subscribe_results"
    },

    dataset: null,

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function(search) {
        this.search = search;
        this.search.dataset.data.bind("reset", this.render);
    },

    render: function() {
        // Don't render search results if there was no search
        if (!this.search.query) {
            return;
        }
        
        var context = PANDA.utils.make_context(this.search.dataset.data.meta);

        context["query"] = this.search.query;
        context["query_human"] = this.search.encode_human_readable();
        context["since"] = this.search.since;
        context["solr_query"] = this.search.make_solr_query()

        if (this.search.since) {
            context["all_results_url"] = "#dataset/" + this.search.dataset.get("slug") + "/search/" + this.search.encode_query_string();
        }

        context["root_url"] = "#dataset/" + this.search.dataset.get("slug") + "/search/" + this.search.encode_query_string() + "/" + this.search.since;
        context["pager_unit"] = "row";
        context["row_count"] = this.search.dataset.get("row_count");
        context["dataset"] = this.search.dataset.results();

        context["pager"] = PANDA.templates.inline_pager(context);

        this.$el.html(PANDA.templates.dataset_results(context));
    },
    
    export_results: function() {
        /*
         * Export complete dataset to CSV asynchronously.
         */
        this.search.dataset.export_data(
            this.search.make_solr_query(),
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
    },
    
    subscribe_results: function() {
        /*
         * Subscribe to search results.
         */
        sub = new PANDA.models.SearchSubscription({
            dataset: this.search.dataset.id,
            query: this.search.make_solr_query(),
            query_url: this.search.encode_query_string(),
            query_human: this.search.encode_human_readable()
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
    }
});
