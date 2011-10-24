PANDA.views.Upload = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.upload,

    file_uploader: null,

    initialize: function() {
        _.bindAll(this, "render");
        
        this.render();

        this.file_uploader = new qq.FileUploaderBasic({
            action: "/upload/",
            button: $("#upload")[0],
            multiple: false,
            onProgress: function(id, fileName, loaded, total) {
                pct = Math.floor(loaded / total * 100);
                $("#progress").text(pct + "%");
            },
            onComplete: function(id, fileName, responseJSON) {
                if(responseJSON.success) {
                    // Create a dataset and relate it to the upload
                    d = new PANDA.models.Dataset({
                        name: fileName,
                        data_upload: responseJSON 
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

