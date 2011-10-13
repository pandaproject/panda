PANDA.views.EditDataset = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.edit_dataset,
    dataset: null,
    data_upload: null,

    events: {
        "click #dataset-save":      "save",
        "click #dataset-download":  "download"
    },

    initialize: function(options) {
        this.dataset = options.dataset;

        this.dataset.fetch_data_upload(_.bind(function(upload) {
            this.data_upload = upload;
            $("#dataset-download").removeAttr('disabled');
        }, this));

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

    download: function() {
        this.data_upload.download(); 
    }
});

