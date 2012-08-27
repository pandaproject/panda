PANDA.views.Home = Backbone.View.extend({
    initialize: function(options) {
        _.bindAll(this);
    },

    text: {
        recently_added_datasets: gettext("Recently added datasets"),
        created_timestamp: gettext("Created %(timeago)s"),
        browse_all_datasets: gettext("Browse all %(count)s datasets"),
        dashboard_link: gettext("Want to see how your PANDA is being used? Visit the <a %(link)s>Dashboard</a>!")
    },

    render: function() {
        var recent_datasets = new PANDA.collections.Datasets()

        recent_datasets.fetch({
            data: { limit: 5 },
            success: _.bind(function() {
                var context = PANDA.utils.make_context({
                    text: this.text,
                    recent: recent_datasets.results()
                });

                this.$el.html(PANDA.templates.home(context));
            }, this)
        });
    }
});

