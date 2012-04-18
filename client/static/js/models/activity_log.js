PANDA.models.ActivityLog = Backbone.Model.extend({
    /*
    Equivalent of panda.models.ActivityLog.
    */
    urlRoot: PANDA.API + "/activity_log"
});

PANDA.collections.ActivityLogs = Backbone.Collection.extend({
    /*
    A collection of panda.models.ActivityLog equivalents.
    */
    model: PANDA.models.ActivityLog,
    urlRoot: PANDA.API + "/activity_log"
});

