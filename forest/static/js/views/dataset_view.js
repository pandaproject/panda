PANDA.views.DatasetView = Backbone.View.extend({
    initialize: function(options) {
        _.bindAll(this);
        
        $("#dataset-export").live("click", this.export_data);
        $("#dataset-destroy").live("click", this.destroy);
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
    },

    render: function() {
        // Nuke old modals
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

        var context = PANDA.make_context({
            'dataset': this.dataset.toJSON(true),
            'categories': this.dataset.categories.toJSON(),
            'data_uploads_html': data_uploads_html,
            'related_uploads_html': related_uploads_html
        });

        this.el.html(PANDA.templates.dataset_view(context));
    },
    
    export_data: function() {
        this.dataset.export_data(function() {
            bootbox.alert("Your export has been successfully queued. When it is complete you will be emailed a link to download the file.");
        }, function(error) {
            bootbox.alert("<p>Your export failed to start! Please notify your administrator.</p><p>Error:</p><code>" + error.traceback + "</code>");
        });
    },

    destroy: function() {
        this.dataset.destroy({ success: _.bind(function() {
            this.dataset = null;

            Redd.goto_search();
        }, this)});
    },
});

