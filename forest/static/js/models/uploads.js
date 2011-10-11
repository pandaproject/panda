PANDA.models.Upload = Backbone.Model.extend({
    /*
    Equivalent of redd.models.Upload.
    */
    urlRoot: PANDA.API + "/upload",

    download: function() {
        window.location = this.url() + "download";
    }
});

PANDA.collections.Uploads = Backbone.Collection.extend({
    /*
    A collection of redd.models.Upload equivalents.
    */
    model: PANDA.models.Upload,
    url: PANDA.API + "/upload"
});


