window.PANDAController = {
    /* Not a controller in the Backbone sense, but a global state manager for the application. */
    init: function() {
        this.data = new PANDA.models.Data();
        this.search = new PANDA.views.Search({ collection: this.data });
        this.router = new PANDA.routers.Index();

        Backbone.history.start();

        return this;
    }
}
