PANDA.views.EditDataset = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.edit_dataset,
    dataset: null,

    events: {
        "click #dataset-save":      "save"
    },

    initialize: function() {
        _.bindAll(this, "render", "save", "destroy");

        $("#dataset-destroy").live("click", this.destroy);
    },

    reset: function() {
        this.render();
    },

    render: function() {
        this.el.html(this.template(this.dataset.toJSON()));

        task = this.dataset.current_task;

        if (task && task.get("task_name") == "redd.tasks.DatasetImportTask") {
            if (task.get("status") == "STARTED") {
                $("#edit-dataset-alert").alert("info block-message", "<p><strong>Import in progress!</strong> This dataset is currently being made searchable. It will not yet appear in search results.</p>Status of import: " + task.get("message") + ".");
            } else if (task.get("status") == "PENDING") {
                $("#edit-dataset-alert").alert("info block-message", "<p><strong>Queued for import!</strong> This dataset is currently waiting to be made searchable. It will not yet appear in search results.</p>");
            } else if (task.get("status") == "FAILURE") {
                $("#edit-dataset-alert").alert("error block-message", '<p><strong>Import failed!</strong> The process to make this dataset searchable failed. It will not appear in search results. <input type="button" class="btn inline" data-controls-modal="dataset-traceback-modal" data-backdrop="true" data-keyboard="true" value="Show detailed error message" />');
            } 
        }
    },

    save: function() {
        form_values = $("#edit-dataset-form").serializeObject();

        s = {};

        _.each(form_values, _.bind(function(v, k) {
            s[k] = v;
        }, this));

        this.dataset.save(s, { success: function() {
            $("#edit-dataset-alert").alert("success", "Saved!");
        }});

        return false;
    },

    destroy: function() {
        this.dataset.destroy({ success: _.bind(function() {
            this.dataset = null;
            window.location = '#datasets';
        }, this)});
    }
});

