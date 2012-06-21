PANDA.models.Export = Backbone.Model.extend({
    /*
    Equivalent of panda.models.Export.
    */
    urlRoot: PANDA.API + "/export"
});

PANDA.collections.Exports = Backbone.Collection.extend({
    /*
    A collection of panda.models.Export equivalents.
    */
    model: PANDA.models.ActivityLog,
    urlRoot: PANDA.API + "/export"
});

