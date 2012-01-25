CustomUploadButton = {
    /*
     * Dummy version of Valum's file uploader widget.
     * Overrides most everything so I can use a simple file widget.
     */
    init: function(o) {
        this._options = {
            onChange: function(input) {}                      
        };

        qq.extend(this._options, o);

        this._input =  $("#upload-file")[0];

        qq.attach(this._input, 'change', _.bind(function() {
            this._options.onChange(this._input);
        }, this)); 

        return this;
    },

    reset: function() {
        // It appears unnecessary to implement this.
    }
}

PANDA.views.DataUpload = Backbone.View.extend({
    el: $("#content"),

    events: {
        "click #upload-continue":      "continue_event",
        "click #upload-start-over":    "start_over_event"
    },
    
    file_uploader: null,
    dataset: null,
    upload: null,
    dataset_is_new: false,

    initialize: function() {
        _.bindAll(this, "render", "on_submit", "on_progress", "on_complete", "step_one_error_message", "step_two_error_message", "step_one", "step_two", "step_three", "continue_event", "start_over_event");
    },

    reset: function(dataset_slug) {
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

        this.el.html(PANDA.templates.data_upload({ dataset: dataset_json }));

        this.file_uploader = new qq.FileUploaderBasic({
            action: "/data_upload/",
            multiple: false,
            allowedExtensions: ["csv", "xls", "xlsx"],
            onSubmit: this.on_submit,
            onProgress: this.on_progress,
            onComplete: this.on_complete,
            showMessage: this.step_one_error_message,
            maxSizeLimit: 1024 * 1024 * 1024,   // 1 GB
            messages: {
                typeError: "{file} is not a supported type. Only CSV, XLS, and XLSX files are currently supported.",
                sizeError: "{file} is too large, the maximum file size is 1 gigabyte.",
                emptyError: "{file} is empty.",
                onLeave: "Your file is being uploaded, if you leave now the upload will be cancelled."
            }
        });
        
        this.create_upload_button();
    },

    create_upload_button: function() {
        $("#upload-file-wrapper").html('<input type="file" id="upload-file" />');

        var btn = CustomUploadButton.init({
            onChange: _.bind(function(input) {
                this.file_uploader._onInputChange(input);
            }, this)
        });

        this.file_uploader._button = btn;
    },

    on_submit: function(id, fileName) {
        /*
         * Handler for when a file upload starts.
         */
        if (!this.dataset) {
            this.dataset = new PANDA.models.Dataset({
                name: fileName.substr(0, fileName.lastIndexOf('.')) || fileName
            });

            this.dataset.save({}, { async: false })
        }

        this.file_uploader.setParams({ dataset_slug: this.dataset.get("slug") }); 

        this.step_two(fileName);
    },

    on_progress: function(id, fileName, loaded, total) {
        /*
         * Handler for when a file upload reports its progress.
         */
        var pct = Math.floor(loaded / total * 100);

        // Don't render 100% until ajax request creating dataset has finished
        if (pct == 100) {
            pct = 99;
        }

        $("#upload-progress .progress-value").css("width", pct + "%");
        $("#upload-progress .progress-text").html('<strong>' + pct + '%</strong> uploaded');
    },

    on_complete: function(id, fileName, responseJSON) {
        /*
         * Handler for when a file upload is completed.
         */
        if (responseJSON.success) {
            this.upload = new PANDA.models.DataUpload(responseJSON);

            // Finish progress bar
            $("#upload-progress .progress-value").css("width", "100%");
            $("#upload-progress .progress-text").html("<strong>100%</strong> uploaded");

            this.step_three();
        } else if (responseJSON.forbidden) {
            Redd.goto_login(window.location.hash);
        } else {
            this.step_one_error_message("Upload failed!");
        }
    },

    step_one_error_message: function(message) {
        $("#upload-file").attr("disabled", true);
        $("#step-1-alert").alert("error", "<p>" + message + ' <input id="step-1-start-over" type="button" class="btn" value="Try again" /></p>' , false);
        $("#step-1-start-over").click(this.step_one);
    },

    step_two_error_message: function(message) {
        $("#step-2-alert").alert("error", "<p>" + message + ' <input id="step-2-start-over" type="button" class="btn" value="Try again" /></p>' , false);
        $("#step-2-start-over").click(this.step_one);
    },

    step_one: function() {
        $(".alert-message").hide();
        $("#step-2").addClass("disabled");
        $("#step-2 .notes").hide();
        this.on_progress(null, null, 0, 1);
        $("#step-3 .sample-data").empty();
        $("#step-3").addClass("disabled");
        $("#upload-continue").attr("disabled", true);
        $("#upload-start-over").attr("disabled", true);
        
        $("#step-1").removeClass("disabled");

        $("#upload-file").remove();
        this.create_upload_button();
    },

    step_two: function(fileName) {
        $("#step-1").addClass("disabled");
        $("#upload-file").attr("disabled", true);
        $("#step-3 .sample-data").empty();
        $("#step-3").addClass("disabled");
        $("#upload-continue").attr("disabled", true);
        $("#upload-start-over").attr("disabled", true);

        var ext = fileName.substr(fileName.lastIndexOf('.') + 1);

        if (ext == 'xls' || ext == 'xlsx') {
            $("#step-2 .notes.xls").show();
        }

        $("#step-2").removeClass("disabled");
    },

    step_three: function() {
        $("#step-2").addClass("disabled");

        sample_data_html = PANDA.templates.inline_sample_data(this.upload.toJSON()); 
        $("#step-3 .sample-data").html(sample_data_html);

        $("#step-3").removeClass("disabled");
        $("#upload-continue").attr("disabled", false);
        $("#upload-start-over").attr("disabled", false);
    },

    continue_event: function() {
        // Begin import, runs synchronously so errors may be caught immediately
        this.dataset.import_data(
            this.upload.get("id"),
            _.bind(function() {
                    Redd.goto_dataset_edit(this.dataset.get("slug"));
            }, this),
            _.bind(function(error) {
                // Preemptive import errors (mismatched columns, wrong file type, etc.)
                this.upload.destroy()
                this.step_one_error_message(error.error_message);
            }, this)
        );
    },

    start_over_event: function() {
        this.upload.destroy({ async: false });

        if (this.dataset_is_new) {
            this.dataset.destroy({ async: false });
        }
        
        this.reset();
    }
});

