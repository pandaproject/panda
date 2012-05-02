PANDA.views.SearchResults = Backbone.View.extend({
    initialize: function(options) {
        _.bindAll(this);

        this.search = options.search;

        this.collection.bind("reset", this.render);
    },

    render: function() {
        // Nuke old modals
        $("#modal-export-search-results").remove();

        var context = PANDA.utils.make_context(this.collection.meta);

        context["query"] = this.search.query,
        context["root_url"] = "#search/" + this.search.query;
        context["pager_unit"] = "dataset";
        context["row_count"] = null;
        context["datasets"] = this.collection.results();

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
                bootbox.alert("Your export has been successfully queued. When it is complete you will be emailed a link to download the file.");
            }, this),
            error: function(xhr, textStatus) {
                error = JSON.parse(xhr.responseText);
                bootbox.alert("<p>Your export failed to start!</p><p>Error:</p><code>" + error.traceback + "</code>");
            }
        });
    }
});

