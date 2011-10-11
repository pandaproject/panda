window.PANDAController = {
    router: null,

    init: function() {
        this.router = new PANDA.routers.Index();

        Backbone.history.start();

        return this;
    }
}
