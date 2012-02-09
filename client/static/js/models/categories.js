PANDA.models.Category = Backbone.Model.extend({
    /*
    Equivalent of panda.models.Category.
    */
    urlRoot: PANDA.API + "/category"
});

PANDA.collections.Categories = Backbone.Collection.extend({
    /*
    A collection of panda.models.Category equivalents.
    */
    model: PANDA.models.Category,
    urlRoot: PANDA.API + "/category",

    comparator: function(category) {
        /*
         * Ensure categories render in alphabetical order.
         */
        return category.get("name");
    }
});


