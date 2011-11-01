PANDA.views.ListDatasets = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.list_datasets,
    pager_template: PANDA.templates.pager,
    dataset_template: PANDA.templates.dataset_block,

    initialize: function(options) {
        _.bindAll(this, "render");

        this.collection = new PANDA.collections.Datasets();
        this.collection.bind("reset", this.render);
    },

    reset: function(limit, page) {
        // TKTK
        this.collection.fetch();
    },

    render: function() {
        context = this.collection.meta;
        context["settings"] = PANDA.settings;

        context["pager"] = this.pager_template(context);
        context["datasets"] = _.map(this.collection.results().datasets, function(d) {
            // Mutate datasets to use sample data for rendering
            d["data"] = _.map(d["sample_data"], function(data) {
                return { data: data };
            });

            d["meta"] = {
                page: 1,
                limit: d["data"].length,
                offset: 0,
                next: null,
                previous: null,
                total_count: d["data"].length,
                is_sample: true
            }

            return d;
        });

        context["dataset_template"] = this.dataset_template;

        this.el.html(this.template(context));
    }
});


