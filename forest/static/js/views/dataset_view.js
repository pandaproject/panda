PANDA.views.DatasetView = Backbone.View.extend({
    template: PANDA.templates.dataset_view,
    data_upload_template: PANDA.templates.data_upload_item,
    related_upload_template: PANDA.templates.related_upload_item,

    initialize: function(options) {
        _.bindAll(this, "render");
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
    },

    render: function() {
        data_uploads_html = this.dataset.data_uploads.map(_.bind(function(data_upload) {
            return this.data_upload_template(data_upload.toJSON());
        }, this));

        related_uploads_html = this.dataset.related_uploads.map(_.bind(function(related_upload) {
            return this.related_upload_template(related_upload.toJSON());
        }, this));

        context = {
            'dataset': this.dataset.toJSON(true),
            'categories': Redd.get_categories().toJSON(),
            'data_uploads_html': data_uploads_html,
            'related_uploads_html': related_uploads_html
        }

        this.el.html(this.template(context));
    }
});

