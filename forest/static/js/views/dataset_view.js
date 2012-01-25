PANDA.views.DatasetView = Backbone.View.extend({
    initialize: function(options) {
        _.bindAll(this);
        
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

            return PANDA.templates.data_upload_item(context);
        }, this));

        related_uploads_html = this.dataset.related_uploads.map(_.bind(function(related_upload) {
            context = {
                editable: false,
                upload: related_upload.toJSON()
            }

            return PANDA.templates.related_upload_item(context);
        }, this));

        context = {
            'dataset': this.dataset.toJSON(true),
            'categories': this.dataset.categories.toJSON(),
            'data_uploads_html': data_uploads_html,
            'related_uploads_html': related_uploads_html
        }

        // Nuke old modals
        $("#modal-dataset-traceback").remove();
        $("#modal-export-dataset").remove();

        this.el.html(PANDA.templates.dataset_view(context));

        var task = this.dataset.current_task;

        if (task && task.get("task_name").startsWith("redd.tasks.import")) {
            if (task.get("status") == "STARTED") {
                $("#edit-dataset-form .alert-message").alert("info block-message", "<p><strong>Import in progress!</strong> This dataset is currently being made searchable. It will not yet appear in search results.</p>Status of import: " + task.get("message") + ".");
            } else if (task.get("status") == "PENDING") {
                $("#edit-dataset-form .alert-message").alert("info block-message", "<p><strong>Queued for import!</strong> This dataset is currently waiting to be made searchable. It will not yet appear in search results.</p>");
            } else if (task.get("status") == "FAILURE") {
                $("#edit-dataset-form .alert-message").alert("error block-message", '<p><strong>Import failed!</strong> The process to make this dataset searchable failed. It will not appear in search results. <input type="button" class="btn inline" data-controls-modal="modal-dataset-traceback" data-backdrop="true" data-keyboard="true" value="Show detailed error message" /></p>');
            } 
        }
    },
    
    export_data: function() {
        this.dataset.export_data(function() {
            bootbox.alert("Your export has been successfully queued. When it is complete you will be emailed a link to download the file.");
        }, function(error) {
            bootbox.alert("<p>Your export failed to start! Please notify your administrator.</p><p>Error:</p><code>" + error.traceback + "</code>");
        });
    }
});

