PANDA.views.EditDataset = Backbone.View.extend({
    el: $("#content"),
    
    template: JST.edit_dataset,
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

        this.dataset.set(form_values);
        this.dataset.save();

        return false;
    }
});

