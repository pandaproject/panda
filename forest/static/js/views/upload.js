PANDA.views.Upload = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.upload,

    file_uploader: null,

    initialize: function() {
        _.bindAll(this, "render");
        
        this.render();

        this.file_uploader = new qq.FileUploader({
            action: "/upload/",
            element: $("#upload")[0],
            multiple: false,
            onComplete: function(id, fileName, responseJSON) {
                if(responseJSON.success) {
                    // Create a dataset and relate it to the upload
                    d = new PANDA.models.Dataset({
                        name: fileName,
                        data_upload: responseJSON["resource_uri"]
                    });

                    // Save the new dataset
                    d.save({}, { success: function() {
                        // Once saved immediately begin importing it
                        d.import_data(function() {
                            // Redirect to the dataset's page
                            window.location = "#dataset/" + d.get("id");
                        });
                    }});
                } else {
                    alert("Upload failed!");
                }
            }
        });
    },

    render: function() {
        this.el.html(this.template());
    }
});

