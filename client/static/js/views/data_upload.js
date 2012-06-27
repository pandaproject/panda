CustomUploadButton = {
    /*
     * Dummy version of Valum's file uploader widget.
     * Overrides everything so I can use a simple file widget.
     * Only necessary so as not to throw errors.
     */
    init: function(o) {
        return this;
    },

    reset: function() {
    }
}

PANDA.views.DataUpload = Backbone.View.extend({
    events: {
        "click #upload-begin":         "begin_event",
        "click #upload-continue":      "continue_event",
        "click #upload-finish":        "finish_event",
        "click #upload-start-over":    "start_over_event",
        "click #step-1-start-over":    "start_over_event",
        "click #step-2-start-over":    "start_over_event",
        "click #step-3-start-over":    "start_over_event"
    },
    
    file_uploader: null,
    dataset: null,
    upload: null,
    dataset_is_new: false,
    available_space: null,

    initialize: function() {
        _.bindAll(this);
    },

    reset: function(dataset_slug) {
        this.file_uploader = null;
        this.upload = null;

        $.ajax({
            url: '/check_available_space/',
            dataType: 'json',
            type: 'GET',
            async: false,
            success: _.bind(function(data, status, xhr) {
                this.available_space = $.parseJSON(xhr.responseText);
            }, this),
            error: _.bind(function(xhr, status, error) {
                this.available_space = null;
            }, this)
        }); 

        if (dataset_slug) {
            this.dataset_is_new = false;
            this.dataset = new PANDA.models.Dataset({ resource_uri: PANDA.API + "/dataset/" + dataset_slug + "/" });

            this.dataset.fetch({
                async: false,
                success: _.bind(function(model, response) {
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
        } else {
            this.dataset_is_new = true;
            this.dataset = null;
            this.render();
        }
    },

    render: function() {
        if (this.dataset) {
            var dataset_json = this.dataset.toJSON();
        } else {
            var dataset_json = null;
        }

        var all_categories = _.reject(Redd.get_categories().toJSON(), function(c) {
            return (c.id == PANDA.settings.UNCATEGORIZED_ID);
        });

        var context = PANDA.utils.make_context({
            dataset: dataset_json,
            available_space: this.available_space,
            all_categories:  all_categories
        });

        this.$el.html(PANDA.templates.data_upload(context));
        
        $('a[rel="popover"]').popover();

        this.file_uploader = new qq.FileUploaderBasic({
            action: "/data_upload/",
            multiple: false,
            allowedExtensions: ["csv", "xls", "xlsx"],
            onSubmit: this.on_submit,
            onProgress: this.on_progress,
            onComplete: this.on_complete,
            showMessage: this.step_one_error_message,
            sizeLimit: PANDA.settings.MAX_UPLOAD_SIZE,
            messages: {
                typeError: "{file} is not a supported type. Only CSV, XLS, and XLSX files are currently supported.",
                sizeError: "{file} is too large, the maximum file size is " + PANDA.settings.MAX_UPLOAD_SIZE + " bytes.",
                emptyError: "{file} is empty.",
                onLeave: "Your file is being uploaded, if you leave now the upload will be cancelled."
            }
        });
        
        // Create upload button
        var upload_button = CustomUploadButton.init();
        this.file_uploader._button = upload_button;

        $("#upload-file").bind("change", this.on_file_selected);
    },

    on_file_selected: function() {
        var filename = $("#upload-file").val();
        var filepath_parts = $("#upload-file").val().split("\\");
        var filename = filepath_parts[filepath_parts.length - 1];
        var ext = filename.substr(filename.lastIndexOf('.') + 1);
        var no_ext = filename.substr(0, filename.lastIndexOf('.'));
        
        $("#dataset-name").val(no_ext);

        if (ext == 'xls' || ext == 'xlsx') {
            $("#step-1 .notes.xls").show();
        } else {
            $("#step-1 .notes.xls").hide();
        }

        if (ext == 'csv') {
            $(".csv-options").show();
        } else {
            $(".csv-options").hide();
        }
    },

    on_submit: function(id, fileName) {
        /*
         * Handler for when a file upload starts.
         */
        var params = {
            encoding: $('#upload-encoding').val()
        }

        if (this.dataset) {
            params["dataset_slug"] = this.dataset.get("slug");
        }
            
        this.file_uploader.setParams(params);

        this.step_two();
    },

    on_progress: function(id, fileName, loaded, total) {
        /*
         * Handler for when a file upload reports its progress.
         *
         * NB: This never files in IE and older FF due to the lack of XHR support.
         */
        var pct = Math.floor(loaded / total * 100);

        $("#step-2 .progress-value").css("width", pct + "%");
        $("#step-2 .progress-value strong").text(pct + "%");
    },

    on_complete: function(id, fileName, responseJSON) {
        /*
         * Handler for when a file upload is completed.
         */
        if (responseJSON.success) {
            this.upload = new PANDA.models.DataUpload(responseJSON);

            // Verify headers match
            if (this.dataset && this.dataset.get("column_schema")) {
                if (!this.upload.get("columns").equals(_.pluck(this.dataset.get("column_schema"), "name"))) {
                    this.step_two_error_message("The columns headers in this file do not match those of the existing data.");
                    return;
                }
            }

            $("#step-2 .ie-progress strong").text("Upload complete!");
            $("#upload-continue").removeAttr("disabled");
        } else if (responseJSON.forbidden) {
            Redd.goto_login(window.location.hash);
        } else if (responseJSON.error_message) {
            this.step_two_error_message(responseJSON.error_message);
        } else if (responseJSON.xhr) {
            this.step_two_error_message(responseJSON.xhr.status + ' ' + responseJSON.xhr.statusText);
        } else {
            this.step_two_error_message('An unexpected error occurred.');
        }
    },

    step_one_error_message: function(message) {
        $("#step-1-alert").alert("alert-error", message + ' <input id="step-1-start-over" type="button" class="btn" value="Try again" />' , false);
    },

    step_two_error_message: function(message) {
        $("#step-2-alert").alert("alert-error", message + ' <input id="step-2-start-over" type="button" class="btn" value="Try again" />' , false);
    },

    step_three_error_message: function(message) {
        $("#step-3-alert").alert("alert-error", message + ' <input id="step-3-start-over" type="button" class="btn" value="Try again" />' , false);
    },

    step_one: function() {
        $(".alert").hide();
        this.on_progress(null, null, 0, 1);
        
        $("#step-1 .notes.xls").hide();
        $(".csv-options").hide();
    },

    step_two: function() {
        $("#upload-continue").attr("disabled", true);
        $("#dataset-name").focus();
        $("#step-2").collapse({ toggle: true, parent: "#steps" });

        // Use fileuploader's Ajax support detection to determine
        // if we can render a progress bar
        if (!qq.UploadHandlerXhr.isSupported()) {
            $("#step-2 .progress-bar").hide();
            $("#step-2 .ie-progress").show();
        }
    },

    step_three: function() {
        sample_data_html = PANDA.templates.inline_sample_data(this.upload.toJSON()); 
        $("#step-3 .sample-data").html(sample_data_html);

        $("#upload-finish").removeAttr("disabled");
        $("#upload-start-over").removeAttr("disabled");

        $("#step-3").collapse({ toggle: true, parent: "#steps" });
    },

    begin_event: function() {
        // Initiate upload
        this.file_uploader._onInputChange($("#upload-file")[0]);
    },

    continue_event: function() {
        this.step_three();
    },

    finish_event: function() {
        $("#upload-finish").attr("disabled", true);
        $("#upload-start-over").attr("disabled", true);

        var fileName = this.upload.get("original_filename");

        var categories = $("#dataset-details-form").serializeObject().categories || new Array();

        // If only a single category is selected it will serialize as a string instead of a list
        if (!_.isArray(categories)) {
            categories = [categories];
        }

        categories = _.map(categories, function(cat) {
            return Redd.get_category_by_slug(cat).clone();
        });

        if (!this.dataset) {
            this.dataset = new PANDA.models.Dataset({
                name: $("#dataset-name").val() || fileName.substr(0, fileName.lastIndexOf('.')) || fileName,
                description: $("#dataset-description").val(),
                categories: categories
            });
            
            this.dataset.save({}, { async: false });
        }

        this.dataset.data_uploads.add(this.upload);
        this.dataset.patch()

        // Begin import, runs synchronously so errors may be caught immediately
        this.dataset.import_data(
            this.upload.get("id"),
            function(dataset) {
                Redd.goto_dataset_view(dataset.get("slug"));
            },
            _.bind(function(dataset, error) {
                // Preemptive import errors (mismatched columns, etc.)
                this.upload.destroy()
                this.step_three_error_message(error.error_message);
            }, this)
        );
    },

    start_over_event: function() {
        $("#upload-finish").attr("disabled", true);
        $("#upload-start-over").attr("disabled", true);

        if (this.upload) {
            this.upload.destroy({ async: false });
            this.upload = null;
        }

        if (this.dataset_is_new && this.dataset) {
            this.dataset.destroy({ async: false });
            this.dataset = null;
        }
        
        if (this.dataset) {
            this.reset(this.dataset.get("slug"));
        } else {
            this.reset();
        }
    }
});

