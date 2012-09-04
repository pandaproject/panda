PANDA.views.RelatedLinks = Backbone.View.extend({
    events: {
        "click .save":          "save",
        "click .add-row":       "add_row",
        "click .remove-row":    "remove_row"
    },

    dataset: null,

    text: PANDA.text.RelatedLinks(),

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function(dataset) {
        this.dataset = dataset;
    },

    render: function() {
        var context = PANDA.utils.make_context({
            text: this.text,
            dataset: this.dataset.toJSON(true)
        });

        this.$el.html(PANDA.templates.modal_related_links(context));

        $("#related-links-form").keypress(_.bind(function(e) {
            if (e.keyCode == 13 && e.target.type != "textarea") {
                this.save(); 
                return false;
            }
        }, this));
    },

    add_row: function() {
        this.$("tbody").append('<tr><td><input type="text" value=""></input></td><td><input type="text" value=""></input></td><td><a class="remove-row" href="#" onclick="return false;"><i class="icon-minus"></i> ' + gettext("Delete row") + '</a></td></tr>');

        return false;
    },

    remove_row: function(e) {
        $(e.currentTarget).closest("tr").remove();
    },

    save: function() {
        /*
         * Save metadata edited via modal.
         */
        var related_links = [];

        var rows = this.$("tbody tr");

        _.each(rows, function(row) {
            var inputs = $(row).find("input");

            var url = $(inputs[0]).val();
            var title = $(inputs[1]).val();

            if (!url) {
                return;
            }
            
            related_links.push({
                url: url,
                title: title
            });
        });

        this.dataset.patch({ related_links: related_links }, 
           function(dataset) {
                $("#modal-related-links").modal("hide");
                Redd.goto_dataset_view(dataset.get("slug"));
            },
            function(dataset, response) {
                try {
                    errors = $.parseJSON(response);
                } catch(e) {
                    errors = { "__all__": gettext("Unknown error") }; 
                }

                $("#related-links-form").show_errors(errors, gettext("Save failed!"));
            }
        );

        return false;
    }
})

