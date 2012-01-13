PANDA.models.RelatedUpload = Backbone.Model.extend({
    /*
    Equivalent of redd.models.RelatedUpload.
    */
    urlRoot: PANDA.API + "/upload"
});

PANDA.collections.RelatedUploads = Backbone.Collection.extend({
    /*
    A collection of redd.models.RelatedUpload equivalents.
    */
    model: PANDA.models.RelatedUpload,
    urlRoot: PANDA.API + "/related_upload"
});


