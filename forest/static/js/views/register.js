PANDA.views.Register = Backbone.View.extend({
    el: $("#content"),
    
    template: PANDA.templates.register,

    events: {
        "submit #register-form":   "register"
    },

    initialize: function() {
        _.bindAll(this, "render");
    },

    reset: function() {
        this.render();
    },

    render: function() {
        this.el.html(this.template());
    },

    register: function() {
        $.ajax({
            url: '/register/',
            dataType: 'json',
            type: 'POST',
            data: $("#register-form").serialize(),
            success: function(data, status, xhr) {
                $.cookie('username', data.username);
                $.cookie('api_key', data.api_key);
                
                Redd.configure_topbar();

                window.location = "#";
            },
            error: function(xhr, status, error) {
                $.cookie('username', null);
                $.cookie('api_key', null);
                
                Redd.configure_topbar();

                try {
                    data = $.parseJSON(xhr.responseText);
                    message = data["message"];
                } catch(e) {
                    message = "Unknown error"; 
                }

                $("#register-alert").alert("error block-message", "<p><strong>Registration failed!</strong> " + message + ".");
            }
        });

        return false;
    },
});



