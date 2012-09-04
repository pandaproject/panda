PANDA.views.SearchResults = Backbone.View.extend({
    events: {
        "click #search-results-export":      "export_results",
        "click #search-results-subscribe":   "subscribe_results"
    },

    search: null,

    text: PANDA.text.SearchResults(),

    text_makers: {
        matching_rows: function(dataset) {
            var text = ngettext("%(count)s matching row (%(row_count)s total rows)", "%(count)s matching rows (%(row_count)s total rows)", dataset.meta.total_count);
            
            return interpolate(text, { count: dataset.meta.total_count, row_count: dataset.row_count }, true);
        }
    },

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function(search) {
        this.search = search
    },

    render: function() {
        var context = PANDA.utils.make_context(this.search.datasets.meta);

        context.text = this.text;
        context.text_makers = this.text_makers;

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
                bootbox.alert(gettext("<p>You will now receive notifications for this search.</p><p>You cancel these notifications on your user page.</p>"));
            }, this),
            error: function(model, response) {
                error = JSON.parse(response);
                bootbox.alert(interpolate(gettext("<p>Failed to subscribe to notifications!</p><p>Error:</p><code>%(traceback)s</code>"), { traceback: error.traceback }, true));
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
                if (PANDA.settings.EMAIL_ENABLED) {
                    note = gettext("Your export has been successfully queued. When it is complete you will be emailed a link to download the file.");
                } else {
                    note = gettext("Your export has been successfully queued. Your PANDA does not have email configured, so you will need to check your Notifications list to see when it is ready to be downloaded.");
                }

                bootbox.alert(note);
            },
            function(error) {
                bootbox.alert(interpolate(gettext("<p>Your export failed to start!</p><p>Error:</p><code>%(traceback)s</code>"), { traceback: error.traceback }, true));
            }
        );
    }
});

