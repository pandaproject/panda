PANDA.views.DatasetEdit = Backbone.View.extend({
    el: $("#content"),
    
    events: {
        "click .actions .dataset-save":     "save"
    },

    related_uploader: null,
    dataset: null,

    initialize: function() {
        _.bindAll(this);

        $("#dataset-destroy").live("click", this.destroy);
        $(".related-uploads .delete").live("click", this.delete_related_upload);
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
        var data_uploads_html = this.dataset.data_uploads.map(_.bind(function(data_upload) {
            var context = {
                upload: data_upload.toJSON()
            }

            return PANDA.templates.inline_data_upload_item(context);
        }, this));

        var related_uploads_html = this.dataset.related_uploads.map(_.bind(function(related_upload) {
            var context = {
                editable: true,
                upload: related_upload.toJSON()
            }

            return PANDA.templates.inline_related_upload_item(context);
        }, this));

        var context = PANDA.make_context({
            'dataset': this.dataset.toJSON(true),
            'categories': Redd.get_categories().toJSON(),
            'data_uploads_html': data_uploads_html,
            'related_uploads_html': related_uploads_html
        });

        // Nuke old modals
        $("#modal-dataset-traceback").remove();
        $("#modal-dataset-destroy").remove();
        $("#modal-related-upload-destroy").remove();

        this.el.html(PANDA.templates.dataset_edit(context));

        var task = this.dataset.current_task;

        if (task && task.get("task_name").startsWith("redd.tasks.import")) {
            if (task.get("status") == "STARTED") {
                $("#edit-dataset-form .alert-message").alert("info block-message", "<p><strong>Import in progress!</strong> This dataset is currently being made searchable. It will not yet appear in search results.</p>Status of import: " + task.get("message") + ".");
            } else if (task.get("status") == "PENDING") {
                $("#edit-dataset-form .alert-message").alert("info block-message", "<p><strong>Queued for import!</strong> This dataset is currently waiting to be made searchable. It will not yet appear in search results.</p>");
            } else if (task.get("status") == "FAILURE") {
                $("#edit-dataset-form .alert-message").alert("error block-message", '<p><strong>Import failed!</strong> The process to make this dataset searchable failed. It will not appear in search results. <input type="button" class="btn inline" data-controls-modal="modal-dataset-traceback" data-backdrop="true" data-keyboard="true" value="Show detailed error message" /></p>');
            } 
        }

        this.related_uploader = new qq.FileUploaderBasic({
            action: "/related_upload/",
            multiple: false,
            onSubmit: this.on_related_upload_submit,
            onProgress: this.on_related_upload_progress,
            onComplete: this.on_related_upload_complete,
            showMessage: this.on_related_upload_message,
            sizeLimit: PANDA.settings.MAX_UPLOAD_SIZE,
            messages: {
                sizeError: "{file} is too large, the maximum file size is " + PANDA.settings.MAX_UPLOAD_SIZE + " bytes.",
                emptyError: "{file} is empty.",
                onLeave: "Your file is being uploaded, if you leave now the upload will be cancelled."
            }
        });
        
        // Create upload button
        var upload_button = CustomUploadButton.init();
        this.related_uploader._button = upload_button;

        $("#upload-related-file").bind("change", this.on_file_selected);
    },

    on_file_selected: function() {
        // Initiate upload
        this.related_uploader._onInputChange($("#upload-related-file")[0]);
    },

    on_related_upload_submit: function(id, fileName) {
        /*
         * Handler for when a file upload starts.
         */
        this.related_uploader.setParams({ dataset_slug: this.dataset.get("slug") }); 

        $("#related-upload-progress").show()
    },

    on_related_upload_progress: function(id, fileName, loaded, total) {
        /*
         * Handler for when a file upload reports its progress.
         */
        var pct = Math.floor(loaded / total * 100);

        // Don't render 100% until ajax request creating dataset has finished
        if (pct == 100) {
            pct = 99;
        }

        $("#related-upload-progress .progress-value").css("width", pct + "%");
        $("#related-upload-progress .progress-text").html('<strong>' + pct + '%</strong> uploaded');
    },

    on_related_upload_complete: function(id, fileName, responseJSON) {
        /*
         * Handler for when a file upload is completed.
         */
        if (responseJSON.success) {
            // Finish progress bar
            $("#related-upload-progress").hide()

            var related_upload = new PANDA.models.RelatedUpload(responseJSON);
            this.dataset.related_uploads.add(related_upload);

            $(".related-uploads").append(PANDA.templates.inline_related_upload_item({ 
                editable: true,
                upload: related_upload.toJSON()
            }));
        } else if (responseJSON.forbidden) {
            Redd.goto_login(window.location.hash);
        } else {
            $("#related-upload-progress").hide()
            this.on_related_upload_message("Upload failed!");
        }
    },

    on_related_upload_message: function(message) {
        alert("yo");
        $("#related-upload-alert").alert("error", "<p>" + message + '</p>' , false);
    },

    save: function() {
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
    },

    delete_related_upload: function(e) {
        var element = $(e.currentTarget)
        var uri = element.attr("data-uri"); 
        var upload = this.dataset.related_uploads.get(uri);

        $("#modal-related-upload-destroy").html(PANDA.templates.modal_related_upload_destroy({ upload: upload.toJSON() }));

        $("#related-upload-destroy").click(function() {
            upload.destroy();
            element.parent("li").remove();

            $("#modal-related-upload-destroy").modal("hide");

            return false;
        });

        $("#modal-related-upload-destroy").modal("show");

        return false;
    }
});

