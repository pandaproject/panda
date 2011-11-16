PANDA.views.ListDatasets = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.list_datasets,
    pager_template: PANDA.templates.pager,
    dataset_template: PANDA.templates.dataset_block,

    category: null,

    initialize: function(options) {
        _.bindAll(this, "render");

        this.collection = new PANDA.collections.Datasets();
        this.collection.bind("reset", this.render);
    },

    reset: function(category, limit, page) {
        if (!limit) {
            limit = PANDA.settings.PANDA_DEFAULT_SEARCH_ROWS;
        }
        
        if (!page) {
            page = 1
        }

        data = {
            limit: limit,
            offset: limit * (page - 1)
        };

        if (category) {
            // This could fail if the category was just created, but that's unlikely.
            this.category = Redd.get_category_by_id(category);
            data["categories"] = this.category.get("id");
        } else {
            this.category = null;
        }

        this.collection.fetch({ async: false, data: data });
    },

    render: function() {
        context = this.collection.meta;
        context["settings"] = PANDA.settings;
        
        context["root_url"] = "#datasets";

        if (this.category) {
            context["category"] = this.category.toJSON();
        } else {
            context["category"] = null;
        }

        context["pager"] = this.pager_template(context);
        context["datasets"] = _.map(this.collection.results().datasets, function(d) {
            d["data"] = d["sample_data"];

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


