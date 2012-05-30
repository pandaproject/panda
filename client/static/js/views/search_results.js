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

        var context = PANDA.utils.make_context(this.datasets.meta);

        context["query"] = this.search.query,
        context["root_url"] = "#search/" + this.search.query + "/" + this.search.since;
        context["pager_unit"] = "dataset";
        context["row_count"] = null;
        context["datasets"] = this.datasets.results();

        context["pager"] = PANDA.templates.inline_pager(context);

        this.el.html(PANDA.templates.search_results(context));

        $("#search-results-export").click(this.export_results);
    },
    
    export_results: function() {
        /*
         * Export complete dataset to CSV files asynchronously.
         */
        data = {
            q: this.search.query
        };

        Redd.ajax({
            url: PANDA.API + "/data/export/",
            dataType: "json",
            data: data,
            success: _.bind(function(response) {
                var note = "Your export has been successfully queued.";

                if (PANDA.settings.EMAIL_ENABLED) {
                    note += " When it is complete you will be emailed a link to download the file."
                } else {
                    note += " Your PANDA does not have email configured, so you will need to check your Notifications list to see when it is ready to be downloaded."
                }

                bootbox.alert(note);
            }, this),
            error: function(xhr, textStatus) {
                error = JSON.parse(xhr.responseText);
                bootbox.alert("<p>Your export failed to start!</p><p>Error:</p><code>" + error.traceback + "</code>");
            }
        });
    }
});

