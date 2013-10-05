PANDA.views.Login = Backbone.View.extend({
    events: {
        "submit #login-form":           "login",
        "click #send-forgot-password":  "send_forgot_password"
    },

    next: null,

    text: PANDA.text.Login(),

    initialize: function() {
        _.bindAll(this);
    },

    reset: function(next) {
        this.next = next;
        this.render();
    },

    render: function() {
        var email = $.cookie("email");

        var context = PANDA.utils.make_context({
            text: this.text,
            email: email
        });

        this.$el.html(PANDA.templates.login(context));

        $("#forgot-password-form").keypress(_.bind(function(e) {
            if (e.keyCode == 13 && e.target.type != "textarea") {
                this.send_forgot_password(); 
            }
        }, this));

        $('#modal-forgot-password').on('shown', function () {
            $("#forgot-email").focus();
        })
    },

    validate: function() {
        var data = $("#login-form").serializeObject();
        var errors = {};

        if (!data["email"]) {
            errors["email"] = [gettext("Please enter your email.")];
        }

        if (!data["password"]) {
            errors["password"] = [gettext("Please enter your password.")];
        }

        return errors;
    },

    login: function() {
        var errors = this.validate();

        if (!_.isEmpty(errors)) {
            $("#login-form").show_errors(errors, gettext("Login failed!"));
        
            return false;
        }

        $.ajax({
            url: '/login/',
            dataType: 'json',
            type: 'POST',
            data: $("#login-form").serialize(),
            success: _.bind(function(data, status, xhr) {
                Redd.set_current_user(new PANDA.models.User(data));

                if (!_.isUndefined(this.next) && !_.isNull(this.next)) {
                    window.location.hash = this.next;
                } else {
                    Redd.goto_search("all");
                }
            }, this),
            error: function(xhr, status, error) {
                Redd.set_current_user(null); 

                try {
                    var errors = $.parseJSON(xhr.responseText);
                } catch(e) {
                    var errors = { "__all__": gettext("Unknown error") }; 
                }

                $("#login-form").show_errors(errors, gettext("Login failed!"));
            }
        });

        return false;
    },

    validate_forgot_password: function() {
        var data = $("#forgot-password-form").serializeObject();
        var errors = {};

        if (!data["email"]) {
            errors["email"] = [gettext("Please enter your email.")];
        }

        return errors;
    },

    send_forgot_password: function() {
        var errors = this.validate_forgot_password();

        if (!_.isEmpty(errors)) {
            $("#forgot-password-form").show_errors(errors, gettext("Error!"));
        
            return false;
        }

        $.ajax({
            url: '/forgot_password/',
            dataType: 'json',
            type: 'POST',
            data: $("#forgot-password-form").serialize(),
            success: _.bind(function(data, status, xhr) {
                bootbox.alert(gettext("Email sent."));
            }, this),
            error: function(xhr, status, error) {
                bootbox.alert(error);
            }
        });
        
        $("#modal-forgot-password").modal("hide");
    }
});


