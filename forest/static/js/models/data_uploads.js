PANDA.models.DataUpload = Backbone.Model.extend({
    /*
    Equivalent of redd.models.DataUpload.
    */
    urlRoot: PANDA.API + "/data_upload"
});

PANDA.collections.DataUploads = Backbone.Collection.extend({
    /*
    A collection of redd.models.DataUpload equivalents.
    */
    model: PANDA.models.DataUpload,
    urlRoot: PANDA.API + "/data_upload"
});


