/* The global PANDA object acts as a registry of PANDA Backbone types. */

window.PANDA = {};
PANDA.API = "/api/1.0";

PANDA.collections = {};
PANDA.models = {};
PANDA.views = {};
PANDA.routers = {};
PANDA.templates = {};
PANDA.bootstrap = {};
PANDA.utils = {};

// A copy of the server-side settings.
// AKA: The simplest thing that works.
PANDA.settings = {
    DEFAULT_SEARCH_GROUPS: 10,
    DEFAULT_SEARCH_ROWS_PER_GROUP: 5, 
    DEFAULT_SEARCH_ROWS: 50,

    NOTIFICATIONS_INTERVAL: 20000,

    MAX_UPLOAD_SIZE: 1024 * 1024 * 1024 // 1 GB
};

PANDA.utils.make_context = function(ctx) {
    /*
     * Context factory function so that PANDA is always in template namespace.
     */
    ctx = ctx || {};
    ctx['PANDA'] = PANDA;

    return ctx;
}

