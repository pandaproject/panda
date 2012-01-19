PANDA.views.DatasetView = Backbone.View.extend({
    template: PANDA.templates.dataset_view,
    data_upload_template: PANDA.templates.data_upload_item,
    related_upload_template: PANDA.templates.related_upload_item,

    initialize: function(options) {
        _.bindAll(this, "render", "export_data");
        
        $("#dataset-export").live("click", this.export_data);
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
    },

    render: function() {
        data_uploads_html = this.dataset.data_uploads.map(_.bind(function(data_upload) {
            context = {
                upload: data_upload.toJSON()
            }

            return this.data_upload_template(context);
        }, this));

        related_uploads_html = this.dataset.related_uploads.map(_.bind(function(related_upload) {
            context = {
                editable: false,
                upload: related_upload.toJSON()
            }

            return this.related_upload_template(context);
        }, this));

        context = {
            'dataset': this.dataset.toJSON(true),
            'categories': this.dataset.categories.toJSON(),
            'data_uploads_html': data_uploads_html,
            'related_uploads_html': related_uploads_html
        }

        this.el.html(this.template(context));
    },
    
    export_data: function() {
        this.dataset.export_data(function() {
            bootbox.alert("Your export has been successfully queued. When it is complete you will be emailed a link to download the file.");
        }, function(error) {
            bootbox.alert("<p>Your export failed to start! Please notify your administrator.</p><p>Error:</p><code>" + error.traceback + "</code>");
        });
    }
});

