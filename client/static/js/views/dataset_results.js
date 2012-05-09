PANDA.views.DatasetResults = Backbone.View.extend({
    dataset: null,

    initialize: function(options) {
        _.bindAll(this);

        this.search = options.search;
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
        this.dataset.data.bind("reset", this.render);
    },

    render: function() {
        // Don't render search results if there was no search
        if (!this.search.query) {
            return;
        }
        
        // Nuke old modals
        $("#modal-export-search-results").remove();

        var context = PANDA.utils.make_context(this.dataset.data.meta);

        context["query"] = this.search.query,
        context["root_url"] = "#dataset/" + this.dataset.get("slug") + "/search/" + this.search.encode_query_string();
        context["pager_unit"] = "row";
        context["row_count"] = this.dataset.get("row_count");
        context["dataset"] = this.dataset.results();

        context["pager"] = PANDA.templates.inline_pager(context);

        this.el.html(PANDA.templates.dataset_results(context));

         $("#search-results-export").click(this.export_results);
    },
    
    export_results: function() {
        /*
         * Export complete dataset to CSV asynchronously.
         */
        this.dataset.export_data(
            this.search.make_solr_query(),
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
