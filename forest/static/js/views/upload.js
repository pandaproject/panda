CustomUploadButton = {
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
        _.bindAll(this, "render", "on_submit", "on_progress", "on_complete");
        
        this.render();

        this.file_uploader = new qq.FileUploaderBasic({
            action: "/upload/",
            /*button: $("#upload")[0],*/
            multiple: false,
            onSubmit: this.on_submit,
            onProgress: this.on_progress,
            onComplete: this.on_complete
        });

        btn = CustomUploadButton.init({
            onChange: _.bind(function(input) {
                this.file_uploader._onInputChange(input);
            }, this)
        });

        this.file_uploader._button = btn;
    },

    render: function() {
        this.el.html(this.template());
    },

    on_submit: function(id, fileName) {
        /*
         * Handler for when a file upload starts.
         */
        $("#upload-filename").val(fileName);

        this.step_two();
    },

    on_progress: function(id, fileName, loaded, total) {
        /*
         * Handler for when a file upload reports its progress.
         */
        pct = Math.floor(loaded / total * 100);
        $("#upload-progress").text(pct);
    },

    on_complete: function(id, fileName, responseJSON) {
        /*
         * Handler for when a file upload is completed.
         */
        if(responseJSON.success) {
            // Create a dataset and relate it to the upload
            this.dataset = new PANDA.models.Dataset({
                name: fileName,
                data_upload: responseJSON 
            });

            // Save the new dataset
            this.dataset.save({}, { success: _.bind(function() {
                // Once saved immediately begin importing it
                this.dataset.import_data(this.step_three);
            }, this)});
        } else {
            // TKTK
            alert("Upload failed!");
        }
    },

    step_one: function() {
        $("#upload-select-file").attr("disabled", false);
        $("#step-2").addClass("disabled");
        $("#step-3").addClass("disabled");
    },

    step_two: function() {
        $("#upload-select-file").attr("disabled", true);
        $("#step-1").addClass("disabled");

        $("#step-2").removeClass("disabled");
    },

    step_three: function() {
        $("#step-2").addClass("disabled");

        $("#upload-continue").attr("disabled", false);
        $("#step-3").removeClass("disabled");
    },

    continue_event: function() {
        window.location = "#dataset/" + this.dataset.get("id");
    }
});

