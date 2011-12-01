PANDA.views.DatasetsResults = Backbone.View.extend({
    template: PANDA.templates.datasets_results,
    pager_template: PANDA.templates.pager,
    view_template: PANDA.templates.datasets_result_modal,

    initialize: function(options) {
        _.bindAll(this, "render", "dataset_link");

        this.search = options.search;
        this.search.datasets.bind("reset", this.render);

        $(".dataset-link").live("click", this.dataset_link);
    },

    render: function() {
        context = this.search.datasets.meta;
        context["settings"] = PANDA.settings;

        context["query"] = this.search.query;
        context["category"] = this.search.category;
        context["root_url"] = "#datasets";

        context["pager"] = this.pager_template(context);
        context["datasets"] = this.search.datasets.results()["datasets"];

        // Remove any lingering modal from previous usage
        $("#dataset-view-modal").remove();

        this.el.html(this.template(context));

        // Recreate modal
        $("#dataset-view-modal").modal({
            keyboard: true
        });
    },

    dataset_link: function(e) {
        dataset_uri = $(e.currentTarget).attr("data-uri");
        dataset = this.search.datasets.get(dataset_uri);

        // Update dataset with complete attributes
        dataset.fetch({ success: _.bind(function(model, response) {
            $("#dataset-view-modal").html(this.view_template(model.toJSON(true)));

            $("#dataset-view-modal #dataset-modal-search-form").submit(function() {
                query = $("#dataset-view-modal #dataset-modal-search-query").val();

                Redd.goto_dataset_search(model.get("id"), query); 
                
                $("#dataset-view-modal").modal("hide");

                return false;
            });

            $("#dataset-view-modal").modal("show");
        }, this) });

        return false;
    }
});


