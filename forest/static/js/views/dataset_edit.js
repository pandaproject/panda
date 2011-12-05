PANDA.views.DatasetEdit = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.dataset_edit,
    dataset: null,

    events: {
        "click .actions .dataset-save":      "save"
    },

    initialize: function() {
        _.bindAll(this, "render", "save", "destroy");

        $("#dataset-destroy").live("click", this.destroy);
    },

    reset: function(slug) {
        this.dataset = new PANDA.models.Dataset({ resource_uri: PANDA.API + "/dataset/" + slug + "/" });

        this.dataset.fetch({
            async: false,
            success: _.bind(function() {
                this.render();
            }, this),
            error: _.bind(function(model, response) {
                if (response.status == 404) {
                    Redd.goto_not_found(); 
                } else {
                    Redd.goto_server_error();
                }
            }, this)
        });
    },

    validate: function() {
        var data = $("#edit-dataset-form").serializeObject();
        var errors = {};

        if (!data["name"]) {
            errors["name"] = ["This field is required."];
        }

        return errors;
    },

    render: function() {
        context = {
            'dataset': this.dataset.toJSON(true),
            'categories': Redd.get_categories().toJSON()
        }

        // Nuke old modals
        $("#dataset-traceback-modal").remove();
        $("#dataset-destroy-modal").remove();

        this.el.html(this.template(context));

        task = this.dataset.current_task;

        if (task && task.get("task_name") == "redd.tasks.DatasetImportTask") {
            if (task.get("status") == "STARTED") {
                $("#edit-dataset-form .alert-message").alert("info block-message", "<p><strong>Import in progress!</strong> This dataset is currently being made searchable. It will not yet appear in search results.</p>Status of import: " + task.get("message") + ".");
            } else if (task.get("status") == "PENDING") {
                $("#edit-dataset-form .alert-message").alert("info block-message", "<p><strong>Queued for import!</strong> This dataset is currently waiting to be made searchable. It will not yet appear in search results.</p>");
            } else if (task.get("status") == "FAILURE") {
                $("#edit-dataset-form .alert-message").alert("error block-message", '<p><strong>Import failed!</strong> The process to make this dataset searchable failed. It will not appear in search results. <input type="button" class="btn inline" data-controls-modal="dataset-traceback-modal" data-backdrop="true" data-keyboard="true" value="Show detailed error message" /></p>');
            } 
        }
    },

    save: function() {
        var errors = this.validate();
        
        if (!_.isEmpty(errors)) {
            $("#edit-dataset-form").show_errors(errors, "Save failed!");
        
            return false;
        }
        
        form_values = $("#edit-dataset-form").serializeObject();

        s = {};

        _.each(form_values, _.bind(function(v, k) {
            if (k == 'categories') {
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

        this.dataset.save(s, {
            success: _.bind(function() {
                Redd.goto_dataset_view(this.dataset.get("slug"));
                window.scrollTo(0, 0);
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

        return false;
    },

    destroy: function() {
        this.dataset.destroy({ success: _.bind(function() {
            this.dataset = null;

            Redd.goto_search();
        }, this)});
    }
});

