/* The global PANDA object acts as a registry of PANDA Backbone types. */

window.PANDA = {};
PANDA.API = "/api/1.0";

PANDA.collections = {};
PANDA.models = {};
PANDA.views = {};
PANDA.routers = {};
PANDA.templates = {};

// A copy of the server-side settings.
// AKA: The simplest thing that works.
PANDA.settings = {
    PANDA_DEFAULT_SEARCH_GROUPS: 10,
    PANDA_DEFAULT_SEARCH_ROWS_PER_GROUP: 5, 
    PANDA_DEFAULT_SEARCH_ROWS: 50
};

