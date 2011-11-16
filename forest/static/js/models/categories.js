PANDA.models.Category = Backbone.Model.extend({
    /*
    Equivalent of redd.models.Category.
    */
    urlRoot: PANDA.API + "/category"
});

PANDA.collections.Categories = Backbone.Collection.extend({
    /*
    A collection of PANDA.models.Category equivalents.
    */
    model: PANDA.models.Category,
    url: PANDA.API + "/category"
});


