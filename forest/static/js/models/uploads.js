PANDA.models.Upload = Backbone.Model.extend({
    /*
    Equivalent of redd.models.Upload.
    */
    urlRoot: PANDA.API + "/upload"
});

PANDA.collections.Uploads = Backbone.Collection.extend({
    /*
    A collection of redd.models.Upload equivalents.
    */
    model: PANDA.models.Upload,
    urlRoot: PANDA.API + "/upload"
});


