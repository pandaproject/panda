PANDA.views.Upload = Backbone.View.extend({
    el: $("#content"),
    
    template: JST.upload,

    file_uploader: null,
    current_dataset: null,

    events: {
        "submit #dataset-form": "create_dataset",
        "submit #import-form": "import_data"
    },

    initialize: function() {
        _.bindAll(this, "render", "create_dataset", "import_data");
        
        this.render();

        this.file_uploader = new qq.FileUploader({
            action: "/ajax_upload/",
            element: $("#upload")[0],
            multiple: false,
            onComplete: function(id, fileName, responseJSON) {
                if(responseJSON.success) {
                    $("#dataset-data-upload").val(responseJSON["id"]);
                    $("#dataset").show();
                } else {
                    alert("Upload failed!");
                }
            }
        });
    },

    render: function() {
        this.el.html(this.template());
    },

    create_dataset: function() {
        this.current_dataset = new PANDA.models.Dataset({
            name: $("#dataset-form #dataset-name").val(),
            data_upload: { id: $("#dataset-form #dataset-data-upload").val() }
        });
        this.current_dataset.save();

        $("#import-form #import-id").val(this.current_dataset.get("id"));
        $("#import").show();

        return false;
    },

    import_data: function() {
        this.current_dataset.import_data(
            function(d) {
                alert(d.get("current_task_id"));
            }
        );

        return false;
    }
});

