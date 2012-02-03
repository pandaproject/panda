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
    el: $("#content"),

    events: {
        "click #upload-begin":         "begin_event",
        "click #upload-continue":      "continue_event",
        "click #upload-start-over":    "start_over_event"
    },
    
    file_uploader: null,
    dataset: null,
    upload: null,
    dataset_is_new: false,

    initialize: function() {
        _.bindAll(this);
    },

    reset: function(dataset_slug) {
        this.file_uploader = null;
        this.upload = null;

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
            dataset_json = this.dataset.toJSON();
        } else {
            dataset_json = null;
        }

        var context = PANDA.utils.make_context({ dataset: dataset_json });

        this.el.html(PANDA.templates.data_upload(context));

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
        var ext = filename.substr(filename.lastIndexOf('.') + 1);

        if (ext == 'xls' || ext == 'xlsx') {
            $("#step-1 .notes.xls").show();
        } else {
            $("#step-1 .notes.xls").hide();
        }

        $("#upload-begin").removeAttr("disabled");
    },

    on_submit: function(id, fileName) {
        /*
         * Handler for when a file upload starts.
         */
        if (this.dataset) {
            this.file_uploader.setParams({ dataset_slug: this.dataset.get("slug") });
        }

        this.step_two();
    },

    on_progress: function(id, fileName, loaded, total) {
        /*
         * Handler for when a file upload reports its progress.
         */
        var pct = Math.floor(loaded / total * 100);

        $(".upload-progress .progress-value").css("width", pct + "%");
        $(".upload-progress .progress-text").html('<strong>' + pct + '%</strong> uploaded');
    },

    on_complete: function(id, fileName, responseJSON) {
        /*
         * Handler for when a file upload is completed.
         */
        if (responseJSON.success) {
            this.upload = new PANDA.models.DataUpload(responseJSON);

            // Verify headers match
            if (this.dataset && this.dataset.get("columns")) {
                if (!this.upload.get("columns").equals(this.dataset.get("columns"))) {
                    this.step_two_error_message("The columns headers in this file do not match those of the existing data.");
                    return;
                }
            }

            this.step_three();
        } else if (responseJSON.forbidden) {
            Redd.goto_login(window.location.hash);
        } else {
            this.step_two_error_message(responseJSON.error_message);
        }
    },

    step_one_error_message: function(message) {
        $("#upload-file").attr("disabled", true);
        $("#step-1-alert").alert("alert-error", message + ' <input id="step-1-start-over" type="button" class="btn" value="Try again" />' , false);
        $("#step-1-start-over").click(this.start_over_event);
    },

    step_two_error_message: function(message) {
        $("#step-2-alert").alert("alert-error", message + ' <input id="step-2-start-over" type="button" class="btn" value="Try again" />' , false);
        $("#step-2-start-over").click(this.start_over_event);
    },

    step_three_error_message: function(message) {
        $("#step-3-alert").alert("alert-error", message + ' <input id="step-3-start-over" type="button" class="btn" value="Try again" />' , false);
        $("#step-3-start-over").click(this.start_over_event);
    },

    step_one: function() {
        $(".alert").hide();
        $("#step-2").addClass("disabled");
        $("#step-2 .notes").hide();
        this.on_progress(null, null, 0, 1);
        $("#step-3 .sample-data").hide();
        $("#step-3 .sample-data").empty();
        $("#step-3").addClass("disabled");
        $("#upload-continue").attr("disabled", true);
        $("#upload-start-over").attr("disabled", true);
        
        $("#upload-file").attr("disabled", false);
        $("#upload-begin").attr("disabled", false);
        $("#step-1").removeClass("disabled");

        $("#step-3").removeClass("well");
        $("#step-1").addClass("well");
    },

    step_two: function() {
        $("#upload-begin").attr("disabled", true);
        $("#step-1").addClass("disabled");
        $("#upload-file").attr("disabled", true);
        
        $("#step-2").removeClass("disabled");
        
        $("#step-1").removeClass("well");
        $("#step-2").addClass("well");
    },

    step_three: function() {
        $("#step-2").addClass("disabled");

        sample_data_html = PANDA.templates.inline_sample_data(this.upload.toJSON()); 
        $("#step-3 .sample-data").html(sample_data_html);
        $("#step-3 .sample-data").show();

        $("#step-3").removeClass("disabled");
        $("#upload-continue").attr("disabled", false);
        $("#upload-start-over").attr("disabled", false);
        
        $("#step-2").removeClass("well");
        $("#step-3").addClass("well");
    },

    begin_event: function() {
        // Initiate upload
        this.file_uploader._onInputChange($("#upload-file")[0]);
    },

    continue_event: function() {
        // Prevent double-clicks
        $("#upload-continue").attr("disabled", true);
        $("#upload-start-over").attr("disabled", true);

        fileName = this.upload.get("original_filename");

        if (!this.dataset) {
            this.dataset = new PANDA.models.Dataset({
                name: fileName.substr(0, fileName.lastIndexOf('.')) || fileName,
            });
            
            this.dataset.save({}, { async: false });
        }

        this.dataset.data_uploads.add(this.upload);
        this.dataset.patch({}, { async: false })

        // Begin import, runs synchronously so errors may be caught immediately
        this.dataset.import_data(
            this.upload.get("id"),
            _.bind(function() {
                    Redd.goto_dataset_view(this.dataset.get("slug"));
            }, this),
            _.bind(function(error) {
                // Preemptive import errors (mismatched columns, etc.)
                this.upload.destroy()
                this.step_three_error_message(error.error_message);
            }, this)
        );
    },

    start_over_event: function() {
        // Prevent double-clicks
        $("#upload-continue").attr("disabled", true);
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

