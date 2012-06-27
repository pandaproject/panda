PANDA.views.RelatedStories = Backbone.View.extend({
    events: {
        "click #related-stories-save":   "save"
    },

    dataset: null,

    initialize: function(options) {
        _.bindAll(this);
    },

    reset: function(dataset) {
        this.dataset = dataset;
    },

    render: function() {
        var context = PANDA.utils.make_context({
            'dataset': this.dataset.toJSON(true),
        });

        this.$el.html(PANDA.templates.modal_related_stories(context));

        $("#related-stories-form").keypress(_.bind(function(e) {
            if (e.keyCode == 13 && e.target.type != "textarea") {
                this.save(); 
                return false;
            }
        }, this));
    },

    validate: function() {
        /*
         * Validate metadata for save.
         */
        var data = $("#related-stories-form").serializeObject();
        var errors = {};

        /*if (!data["name"]) {
            errors["name"] = ["This field is required."];
        }*/

        return errors;
    },

    save: function() {
        /*
         * Save metadata edited via modal.
         */
        var errors = this.validate();
        
        if (!_.isEmpty(errors)) {
            $("#related-stories-form").show_errors(errors, "Save failed!");
        
            return false;
        }
        
        var form_values = $("#t-form").serializeObject();

        var s = {};

        //TODO
        
        this.dataset.patch(s, 
           function(dataset) {
                $("#modal-related-stories").modal("hide");
                Redd.goto_dataset_view(dataset.get("slug"));
            },
            function(dataset, response) {
                try {
                    errors = $.parseJSON(response);
                } catch(e) {
                    errors = { "__all__": "Unknown error" }; 
                }

                $("#related-stories-form").show_errors(errors, "Save failed!");
            }
        );

        return false;
    }
})

