/* The global PANDA object acts as a registry of PANDA Backbone types. */

window.PANDA = {};
PANDA.API = "/api/1.0";

PANDA.collections = {};
PANDA.models = {};
PANDA.views = {};
PANDA.routers = {};
PANDA.templates = {};
PANDA.errors = {};
PANDA.bootstrap = {};
PANDA.utils = {};

// A copy of the server-side settings.
// AKA: The simplest thing that works.
// Mostly populated in index.html.
PANDA.settings = {
    CONTENT_ELEMENT: "#content",
    NOTIFICATIONS_INTERVAL: 20000,
    SLOW_QUERY_TIMEOUT: 10000
};

PANDA.utils.make_context = function(ctx) {
    /*
     * Context factory function so that PANDA is always in template namespace.
     */
    ctx = ctx || {};
    ctx['PANDA'] = PANDA;

    return ctx;
}

PANDA.utils.truncate = function(str, limit) {
    /*
     * From: http://snipplr.com/view.php?codeview&id=16108
     */
	var bits, i;

	bits = str.split('');

	if (bits.length > limit) {
		for (i = bits.length - 1; i > -1; --i) {
			if (i > limit) {
				bits.length = i;
			}
			else if (' ' === bits[i]) {
				bits.length = i;
				break;
			}
		}

		bits.push('...');
	}

	return bits.join('');
}

PANDA.utils.format_file_size = function(size) {
    /*
     * From: http://programanddesign.com/js/human-readable-file-size-in-javascript/
     */
    var units = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    var i = 0;

    while(size >= 1024) {
        size /= 1024;
        ++i;
    }

    return size.toFixed(1) + ' ' + units[i];
}

PANDA.utils.escapes_to_entities = function(escaped_text) {
    return escaped_text.replace(/%(..)/g,"&#x$1;");
};

PANDA.utils.csrf_download = function(url) {
    var iframe = $("<iframe />");
    var form = $('<form action="' + url + '" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="' + $.cookie('csrftoken') + '" /></form>');

    $("body").append(iframe);
    iframe.append(form);
    form.submit();
    iframe.remove();
};

