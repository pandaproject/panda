PANDA.views.DatasetsResults = Backbone.View.extend({
    template: PANDA.templates.datasets_results,
    pager_template: PANDA.templates.pager,
    view_template: PANDA.templates.modal_dataset_search,

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
        $("#modal-dataset-search").remove();

        this.el.html(this.template(context));

        // Enable result sorting
        $("#datasets-results table").tablesorter({
            cssHeader: "no-sort-header",
            cssDesc: "sort-desc-header",
            cssAsc: "sort-asc-header",
            headers: {
                0: { sorter: "text" },
                1: { sorter: false },
                2: { sorter: "text" },
                3: { sorter: false }
            },
            textExtraction: function(node) {
                return $(node).children(".sort-value").text();
            },
            debug: true
        });

        // Create new modal
        $("#modal-dataset-search").modal({
            keyboard: true
        });
    },

    dataset_link: function(e) {
        dataset_uri = $(e.currentTarget).attr("data-uri");
        dataset = this.search.datasets.get(dataset_uri);

        // Update dataset with complete attributes
        dataset.fetch({ success: _.bind(function(model, response) {
            $("#modal-dataset-search").html(this.view_template(model.toJSON(true)));

            $("#modal-dataset-search-form").submit(function() {
                query = $("#modal-dataset-search-query").val();

                Redd.goto_dataset_search(model.get("slug"), query); 
                
                $("#modal-dataset-search").modal("hide");

                return false;
            });

            $("#modal-dataset-search").modal("show");
        }, this) });

        return false;
    }
});


