PANDA.views.EditDataset = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.edit_dataset,
    dataset: null,

    events: {
        "click #dataset-save":      "save",
        "click #dataset-destroy":    "destroy",
        "click #dataset-download":  "download"
    },

    initialize: function(options) {
        this.dataset = options.dataset;

        _.bindAll(this, "render");
        
        this.render();
    },

    render: function() {
        this.el.html(this.template(this.dataset.toJSON()));
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
        this.dataset.destroy({ success: function() {
            window.location = '#datasets'
        }});
    },

    download: function() {
        this.dataset.data_upload.download(); 
    }
});

