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

PANDA.views.Upload = Backbone.View.extend({
    el: $("#content"),

    events: {
        "click #upload-continue":      "continue_event"
    },
    
    template: PANDA.templates.upload,

    file_uploader: null,
    dataset: null,

    initialize: function() {
        _.bindAll(this, "render", "on_submit", "on_progress", "on_complete", "step_one_error_message", "step_two_error_message", "step_one", "step_two", "step_three", "continue_event");
    },

    reset: function() {
        this.render();

        this.file_uploader = new qq.FileUploaderBasic({
            action: "/upload/",
            multiple: false,
            allowedExtensions: ["csv"],
            onSubmit: this.on_submit,
            onProgress: this.on_progress,
            onComplete: this.on_complete,
            showMessage: this.step_one_error_message,
            maxSizeLimit: 1024 * 1024 * 1024,   // 1 GB
            messages: {
                typeError: "{file} is not a supported type. Only CSV files are currently supported.",
                sizeError: "{file} is too large, the maximum file size is 1 gigabyte.",
                //minSizeError: "{file} is too small, minimum file size is {minSizeLimit}.",
                emptyError: "{file} is empty.",
                onLeave: "Your file is being uploaded, if you leave now the upload will be cancelled."
            }
        });

        this.create_upload_button();
    },

    render: function() {
        this.el.html(this.template());
    },

    create_upload_button: function() {
        $("#upload-file-wrapper").html('<input type="file" id="upload-file" />');

        btn = CustomUploadButton.init({
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
        this.step_two();
    },

    on_progress: function(id, fileName, loaded, total) {
        /*
         * Handler for when a file upload reports its progress.
         */
        pct = Math.floor(loaded / total * 100);
        $("#upload-progress .progress-value").css("width", pct + "%");
        $("#upload-progress .progress-text").html('<strong>' + pct + '%</strong> uploaded');
    },

    on_complete: function(id, fileName, responseJSON) {
        /*
         * Handler for when a file upload is completed.
         */
        if (responseJSON.success) {
            // Create a dataset and relate it to the upload
            this.dataset = new PANDA.models.Dataset({
                name: fileName,
                data_upload: responseJSON 
            });

            // Save the new dataset
            this.dataset.save({}, {
                success: _.bind(function() {
                    // Once saved immediately begin importing it
                    this.dataset.import_data(this.step_three);
                }, this),
                error: _.bind(function(modal, response) {
                    error = $.parseJSON(response.responseText);
                    $("#upload-traceback-modal .modal-body").text(error.traceback);
                    this.step_two_error_message('Error creating dataset!&nbsp;<input type="button" class="btn" data-controls-modal="upload-traceback-modal" data-backdrop="true" data-keyboard="true" value="Show detailed error message" />');
                }, this)
            });
        } else if (responseJSON.forbidden) {
            window.location = "#login";
        } else {
            this.step_one_error_message('Upload failed!');
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
        this.on_progress(null, null, 0, 1);
        $("#step-3").addClass("disabled");
        $("#upload-continue").attr("disabled", true);
        
        $("#step-1").removeClass("disabled");

        $("#upload-file").remove();
        this.create_upload_button();
    },

    step_two: function() {
        $("#step-1").addClass("disabled");
        $("#upload-file").attr("disabled", true);
        $("#step-3").addClass("disabled");
        $("#upload-continue").attr("disabled", true);

        $("#step-2").removeClass("disabled");
    },

    step_three: function() {
        $("#step-2").addClass("disabled");

        $("#step-3").removeClass("disabled");
        $("#upload-continue").attr("disabled", false);
    },

    continue_event: function() {
        window.location = "#dataset/" + this.dataset.get("id");
    }
});

