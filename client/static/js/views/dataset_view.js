PANDA.views.DatasetView = Backbone.View.extend({
    edit_view: null,

    initialize: function(options) {
        _.bindAll(this);

        this.edit_view = new PANDA.views.DatasetEdit();

        $(".data-uploads .edit, .related-uploads .edit").live("click", this.edit_upload);
        $(".data-uploads .delete, .related-uploads .delete").live("click", this.delete_upload);
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
        this.edit_view.set_dataset(dataset);
    },

    render: function() {
        // Render inlines
        data_uploads_html = this.dataset.data_uploads.map(_.bind(function(upload) {
            return PANDA.templates.inline_upload_item({
                upload_type: "data",
                upload: upload.toJSON()
            });
        }, this));

        related_uploads_html = this.dataset.related_uploads.map(_.bind(function(upload) {
            return PANDA.templates.inline_upload_item({
                upload_type: "related",
                upload: upload.toJSON()
            });
        }, this));

        sample_data_html = PANDA.templates.inline_sample_data({
            "columns": _.pluck(this.dataset.get("column_schema"), "name"),
            "sample_data": this.dataset.get("sample_data")
        });

        var context = PANDA.utils.make_context({
            'dataset': this.dataset.toJSON(true),
            'categories': this.dataset.categories.toJSON(),
            'all_categories': Redd.get_categories().toJSON(), 
            'data_uploads_html': data_uploads_html,
            'related_uploads_html': related_uploads_html,
            'sample_data_html': sample_data_html
        });

        this.el.html(PANDA.templates.dataset_view(context));
        
        this.edit_view.el = $("#modal-edit-dataset");

        $('#modal-edit-dataset').on('shown', function () {
            $("#dataset-name").focus();
        });

        $('#view-dataset a[rel="tooltip"]').tooltip();

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

        $("#dataset-edit").click(this.edit);
        $("#dataset-upload-related").click(this.upload_related);
        $("#dataset-index-types").click(this.index_types);
        $("#dataset-export").click(this.export_data);
        $("#dataset-destroy").click(this.destroy);
    },

    edit_upload: function(e) {
        /*
         * Provide a modal dialog to allow editing upload metadata. Save that data
         * and refresh the UI.
         */
        var element = $(e.currentTarget).parent("li");
        var uri = element.attr("data-uri"); 
        var upload_type = element.attr("data-type");

        if (upload_type == "data") {
            var upload = this.dataset.data_uploads.get(uri);
        } else {
            var upload = this.dataset.related_uploads.get(uri);
        }

        $("#modal-upload-edit").html(PANDA.templates.modal_upload_edit({ upload: upload.toJSON() }));

        $("#upload-save").click(function() {
            upload.save({ title: $("#upload-title").val() }, { async: false });

            element.replaceWith(
                PANDA.templates.inline_upload_item({ upload_type: upload_type, upload: upload.toJSON() })
            );

            // Enable tooltips on new list item
            $("li[data-uri='" + upload.id + "']").children('a[rel="tooltip"]').tooltip();

            $("#modal-upload-edit").modal("hide");

            return false;
        });

        $("#modal-upload-edit").modal("show");

        return false;
    },

    delete_upload: function(e) {
        var element = $(e.currentTarget).parent("li");
        var uri = element.attr("data-uri"); 
        var upload_type = element.attr("data-type"); 

        if (upload_type == "data") {
            var uploads = this.dataset.data_uploads;
        } else {
            var uploads = this.dataset.related_uploads;
        }
            
        var upload = uploads.get(uri);
            
        var message = "<p>This will irreversibly destroy <strong>" + upload.get("title") + "</strong>. It will not be possible to recover this file.</p>";

        if (upload_type == "data") {
            message += "<p><strong>All data imported from this file will also be deleted.</strong></p>";
        }

        bootbox.dialog(
            message,
            [
                {
                    "label": "Delete",
                    "class": "btn-danger",
                    "callback": _.bind(function(result) {
                        uploads.remove(upload);
                        upload.destroy();
                        element.remove();

                        if (uploads.length == 0) {
                            $("." + upload_type + "-uploads").hide();
                            $("#no-" + upload_type + "-uploads").show();
                        }
                    }, this)
                },
                {
                    "label": "Cancel"
                }
            ]
        );

        return false;
    },

    edit: function() {
        this.edit_view.render();

        $("#modal-edit-dataset").modal("show");
    },

    upload_related: function() {
        /*
         * Upload a related file.
         */
        this.related_uploader._onInputChange($("#upload-related-file")[0]);
        $("#modal-upload-related .modal-footer input").attr("disabled", true); 

        return false;
    },

    on_related_upload_submit: function(id, fileName) {
        /*
         * Handler for when a related upload starts.
         */
        this.related_uploader.setParams({ dataset_slug: this.dataset.get("slug") }); 
        $("#modal-upload-related .progress-bar").show();
    },

    on_related_upload_progress: function(id, fileName, loaded, total) {
        /*
         * Handler for when a related upload reports its progress.
         */
        var pct = Math.floor(loaded / total * 100);

        // Don't render 100% until ajax request creating dataset has finished
        if (pct == 100) {
            pct = 99;
        }

        $("#modal-upload-related .progress-value").css("width", pct + "%");
        $("#modal-upload-related .progress-value strong").html(pct + '%');
    },

    on_related_upload_complete: function(id, fileName, responseJSON) {
        /*
         * Handler for when a related upload is completed.
         */
        if (responseJSON.success) {
            var related_upload = new PANDA.models.RelatedUpload(responseJSON);
            this.dataset.related_uploads.add(related_upload);

            $("#no-related-uploads").hide();
            $(".related-uploads").append(PANDA.templates.inline_upload_item({ 
                upload_type: "related",
                upload: related_upload.toJSON()
            }));
            $(".related-uploads").show();
            
            $('#view-dataset .related-uploads a[rel="tooltip"]').tooltip();

            $("#modal-upload-related").modal("hide")
            $("#modal-upload-related .progress-bar").hide();
            $("#modal-upload-related .modal-footer input").removeAttr("disabled"); 
            this.on_related_upload_progress(null, null, 0, 1);
        } else if (responseJSON.forbidden) {
            Redd.goto_login(window.location.hash);
        } else {
            this.on_related_upload_message("Upload failed!");
            $("#modal-upload-related .modal-footer input").removeAttr("disabled"); 
            this.on_related_upload_progress(null, null, 0, 1);
        }
    },

    on_related_upload_message: function(message) {
        $("#related-upload-alert").alert("alert-error", "<p>" + message + '</p>' , false);
    },

    index_types: function() {
        /*
         * Reindex dataset asynchronously.
         */
        data = $("#typed-columns-form").serializeObject();

        column_types = [];
        typed_columns = [];

        _.each(this.dataset.get("column_schema"), function(c, i) {
            column_types[i] = data["type-" + i];
            typed_columns[i] = ("typed-" + i in data); 
        });

        this.dataset.reindex_data(
            typed_columns,
            column_types,
            function(dataset) {
                var note = "Your data indexing task has been successfully queued.";

                if (PANDA.settings.EMAIL_ENABLED) {
                    note += " You will receive an email when it is complete."
                } else {
                    note += " Your PANDA does not have email configured, so you will need to check your Notifications list to see when the task is complete."
                }

                bootbox.alert(
                    note,
                    function() {
                        Redd.goto_dataset_view(dataset.get("slug"));
                        window.scrollTo(0, 0);
                    }
                );
            },
            function(dataset, error) {
                bootbox.alert("<p>Your data indexing task failed to start!</p><p>Error:</p><code>" + error.traceback + "</code>");
            });
    },
    
    export_data: function() {
        /*
         * Export complete dataset to CSV asynchronously.
         */
        this.dataset.export_data(
            null,
            function(dataset) {
                var note = "Your export has been successfully queued.";

                if (PANDA.settings.EMAIL_ENABLED) {
                    note += " When it is complete you will be emailed a link to download the file."
                } else {
                    note += " Your PANDA does not have email configured, so you will need to check your Notifications list to see when it is ready to be downloaded."
                }

                bootbox.alert(note);
            },
            function(dataset, error) {
                bootbox.alert("<p>Your export failed to start!</p><p>Error:</p><code>" + error.traceback + "</code>");
            }
        );
    },

    destroy: function() {
        /*
         * Destroy this dataset.
         *
         * TODO: error handler
         */
        this.dataset.destroy({
            success: _.bind(function() {
                this.dataset = null;

                Redd.goto_search("all");
            }, this)
        });
    }
});

