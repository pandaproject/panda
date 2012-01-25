/* The global PANDA object acts as a registry of PANDA Backbone types. */

window.PANDA = {};
PANDA.API = "/api/1.0";

PANDA.collections = {};
PANDA.models = {};
PANDA.views = {};
PANDA.routers = {};
PANDA.templates = {};
PANDA.bootstrap = {};

// A copy of the server-side settings.
// AKA: The simplest thing that works.
PANDA.settings = {
    PANDA_DEFAULT_SEARCH_GROUPS: 10,
    PANDA_DEFAULT_SEARCH_ROWS_PER_GROUP: 5, 
    PANDA_DEFAULT_SEARCH_ROWS: 50,

    PANDA_NOTIFICATIONS_INTERVAL: 20000,

    PANDA_SEARCH_HELP_TEXT: "<ul><li>Use an asterisk to match part of a word: <strong>chris*</strong> will match &quot;Chris&quot;, &quot;Christian&quot; or &quot;Christopher&quot;.</li><li>Put phrases in quotes: <strong>&quot;Chicago Bears&quot;</strong> will not match &quot;Chicago Panda Bears&quot;.</li><li>Use AND and OR to find combinations of terms: <strong>homicide AND first</strong> will match &quot;first degree homicide&quot; or &quot;homicide, first degree&quot;, but not just &quot;homicide&quot;.</li><li>Group words with parantheses: <strong>homicide AND (first OR 1st)</strong> will match &quot;1st degree homicide&quot;, &quot;first degree homicide&quot;, or &quot;homicide, first degree&quot;.</li></ul>"
};

PANDA.make_context = function(ctx) {
    /*
     * Context factory function so that PANDA is always in template namespace.
     */
    ctx = ctx || {};
    ctx['PANDA'] = PANDA;

    return ctx;
}
