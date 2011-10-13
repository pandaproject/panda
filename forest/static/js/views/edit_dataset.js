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

        simple_type_prefix = "__schema_simple_type_";
        indexed_prefix = "__schema_indexed_";

        // Zero-out indexed fields since they will be reloaded from checkboxes
        _.each(this.dataset.attributes.schema, function(s) {
            s.indexed = false;
        });

        _.each(form_values, _.bind(function(v, k) {
            if (k.indexOf(simple_type_prefix) == 0) {
                i = k.slice(simple_type_prefix.length);
                this.dataset.attributes.schema[i].simple_type = v;
            } else if (k.indexOf(indexed_prefix) == 0) {
                i = k.slice(indexed_prefix.length);
                this.dataset.attributes.schema[i].indexed = true;
            } else {
                s = {};
                s[k] = v;
                this.dataset.set(s);
            }
        }, this));

        this.dataset.save();

        return false;
    },

    download: function() {
        this.data_upload.download(); 
    }
});

