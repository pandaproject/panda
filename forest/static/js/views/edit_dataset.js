PANDA.views.EditDataset = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.edit_dataset,
    dataset: null,

    events: {
        "submit #edit-dataset-form": "save"
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

        _.each(form_values, _.bind(function(v, k) {
            if (k.indexOf("__schema_") == 0) {
                i = k.slice(9);
                this.dataset.attributes.schema[i][1] = v;
            } else {
                s = {};
                s[k] = v;
                this.dataset.set(s);
            }
        }, this));

        this.dataset.save();

        return false;
    }
});

