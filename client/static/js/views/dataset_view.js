PANDA.views.DatasetView = Backbone.View.extend({
    edit_view: null,

    initialize: function(options) {
        _.bindAll(this);

        this.edit_view = new PANDA.views.DatasetEdit();

        $(".related-uploads .delete").live("click", this.delete_related_upload);
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
        this.edit_view.set_dataset(dataset);
    },

    render: function() {
        // Nuke old modals
        $("#modal-edit-dataset").remove();
        $("#modal-upload-related").remove();
        $("#modal-index-types").remove();
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

    delete_related_upload: function(e) {
        var element = $(e.currentTarget)
        var uri = element.attr("data-uri"); 
        var upload = this.dataset.related_uploads.get(uri);

        $("#modal-related-upload-destroy").html(PANDA.templates.modal_related_upload_destroy({ upload: upload.toJSON() }));

        $("#related-upload-destroy").click(_.bind(function() {
            this.dataset.related_uploads.remove(upload);
            upload.destroy();
            element.parent("li").remove();

            if (this.dataset.related_uploads.length == 0) {
                $(".related-uploads").hide();
                $("#no-related-uploads").show();
            }

            $("#modal-related-upload-destroy").modal("hide");

            return false;
        }, this));

        $("#modal-related-upload-destroy").modal("show");

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
            $(".related-uploads").append(PANDA.templates.inline_related_upload_item({ 
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
        $("#related-upload-alert").alert("error", "<p>" + message + '</p>' , false);
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
            _.bind(function() {
                bootbox.alert(
                    "Your data indexing task has been successfully queued. You wil receive an email when it is complete.",
                    _.bind(function() {
                        Redd.goto_dataset_view(this.dataset.get("slug"));
                        window.scrollTo(0, 0);
                    }, this));
            }, this),
            function(error) {
                bootbox.alert("<p>Your data indexing task failed to start!</p><p>Error:</p><code>" + error.traceback + "</code>");
            });
    },
    
    export_data: function() {
        /*
         * Export complete dataset to CSV asynchronously.
         */
        this.dataset.export_data(function() {
            bootbox.alert("Your export has been successfully queued. When it is complete you will be emailed a link to download the file.");
        }, function(error) {
            bootbox.alert("<p>Your export failed to start!</p><p>Error:</p><code>" + error.traceback + "</code>");
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

