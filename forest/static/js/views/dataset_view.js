PANDA.views.DatasetView = Backbone.View.extend({
    initialize: function(options) {
        _.bindAll(this);
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
    },

    render: function() {
        // Nuke old modals
        $("#modal-edit-dataset").remove();
        $("#modal-upload-related").remove();
        $("#modal-export-dataset").remove();
        $("#modal-dataset-destroy").remove();

        // Render inlines
        data_uploads_html = this.dataset.data_uploads.map(_.bind(function(data_upload) {
            context = {
                upload: data_upload.toJSON()
            }

            return PANDA.templates.inline_data_upload_item(context);
        }, this));

        related_uploads_html = this.dataset.related_uploads.map(_.bind(function(related_upload) {
            context = {
                editable: false,
                upload: related_upload.toJSON()
            }

            return PANDA.templates.inline_related_upload_item(context);
        }, this));

        sample_data_html = PANDA.templates.inline_sample_data(this.dataset.toJSON());

        var context = PANDA.make_context({
            'dataset': this.dataset.toJSON(true),
            'categories': this.dataset.categories.toJSON(),
            'all_categories': Redd.get_categories().toJSON(), 
            'data_uploads_html': data_uploads_html,
            'related_uploads_html': related_uploads_html,
            'sample_data_html': sample_data_html
        });

        this.el.html(PANDA.templates.dataset_view(context));
        
        $("#dataset-save").click(this.save);
        $("#dataset-upload-related").click(this.upload_related);
        $("#dataset-export").click(this.export_data);
        $("#dataset-destroy").click(this.destroy);
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

    save: function() {
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
                this.render();
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
    },

    upload_related: function() {
        /*
         * Upload a related file.
         */
        alert("upload related");
    },
    
    export_data: function() {
        /*
         * Export complete dataset to CSV asynchronously.
         */
        this.dataset.export_data(function() {
            bootbox.alert("Your export has been successfully queued. When it is complete you will be emailed a link to download the file.");
        }, function(error) {
            bootbox.alert("<p>Your export failed to start! Please notify your administrator.</p><p>Error:</p><code>" + error.traceback + "</code>");
        });
    },

    destroy: function() {
        /*
         * Destroy this dataset.
         */
        this.dataset.destroy({ success: _.bind(function() {
            this.dataset = null;

            Redd.goto_search();
        }, this)});
    }
});

