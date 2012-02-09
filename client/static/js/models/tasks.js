PANDA.models.Task = Backbone.Model.extend({
    /*
    Equivalent of panda.models.TaskStatus.
    */
    urlRoot: PANDA.API + "/task"
});

PANDA.collections.Tasks = Backbone.Collection.extend({
    /*
    A collection of panda.models.TaskStatus equivalents.
    */
    model: PANDA.models.Task,
    urlRoot: PANDA.API + "/task"
});


