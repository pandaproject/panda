PANDA.models.Task = Backbone.Model.extend({
    /*
    Equivalent of redd.models.Task.
    */
    urlRoot: PANDA.API + "/task"
});

PANDA.collections.Tasks = Backbone.Collection.extend({
    /*
    A collection of PANDA.models.Task equivalents.
    */
    model: PANDA.models.Task,
    urlRoot: PANDA.API + "/task"
});


