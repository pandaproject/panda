PANDA.views.DatasetEdit = Backbone.View.extend({
    initialize: function(options) {
        _.bindAll(this);
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
    },

    render: function() {
        all_categories = _.reject(Redd.get_categories().toJSON(), function(c) {
            return (c.id == PANDA.settings.UNCATEGORIZED_ID);
        });


        var context = PANDA.utils.make_context({
            'dataset': this.dataset.toJSON(true),
            'categories': this.dataset.categories.toJSON(),
            'all_categories': all_categories 
        });

        this.el.html(PANDA.templates.modal_dataset_edit(context));

        $("#dataset-edit-save").click(this.edit_save);
    },

    validate: function() {
        /*
         * Validate metadata for save.
         */
        var data = $("#edit-dataset-form").serializeObject();
        var errors = {};

        if (!data["name"]) {
            errors["name"] = ["This field is required."];
        }

        return errors;
    },

    edit_save: function() {
        /*
         * Save metadata edited via modal.
         */
        var errors = this.validate();
        
        if (!_.isEmpty(errors)) {
            $("#edit-dataset-form").show_errors(errors, "Save failed!");
        
            return false;
        }
        
        var form_values = $("#edit-dataset-form").serializeObject();

        var s = {};

        // Ensure categories is cleared
        if (!("categories" in form_values)) {
            this.dataset.categories.reset();
        }

        _.each(form_values, _.bind(function(v, k) {
            if (k == "categories") {
                // If only a single category is selected it will serialize as a string instead of a list
                if (!_.isArray(v)) {
                    v = [v];
                }

                categories = _.map(v, function(cat) {
                    return Redd.get_category_by_slug(cat).clone();
                });

                this.dataset.categories.reset(categories);
            } else {
                s[k] = v;
            }
        }, this));

        this.dataset.patch(s, {
            success: _.bind(function() {
                Redd.goto_dataset_view(this.dataset.get("slug"));
                Redd.refresh_categories();
            }, this),
            error: function(model, response) {
                try {
                    errors = $.parseJSON(response);
                } catch(e) {
                    errors = { "__all__": "Unknown error" }; 
                }

                $("#edit-dataset-form").show_errors(errors, "Save failed!");
            }
        });
    }
})

