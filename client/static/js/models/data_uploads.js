PANDA.models.DataUpload = Backbone.Model.extend({
    /*
    Equivalent of panda.models.DataUpload.
    */
    urlRoot: PANDA.API + "/data_upload"
});

PANDA.collections.DataUploads = Backbone.Collection.extend({
    /*
    A collection of panda.models.DataUpload equivalents.
    */
    model: PANDA.models.DataUpload,
    urlRoot: PANDA.API + "/data_upload"
});


