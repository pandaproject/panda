PANDA.text.Inlines = function() {
    /* Text blobs for inlines that are reused in multiple views. */
    return {
        previous: gettext("Previous"),
        next: gettext("Next"),

        matching_rows: function(offset, limit, count) {
            var out = ngettext("%(start)s-%(end)s of %(count)s matching row", "%(start)s-%(end)s of %(count)s matching rows", count);
            
            return interpolate(out, {
                start: offset + 1,
                end: Math.min(offset + limit, count),
                count: count
            }, true);
        },

        total_rows: function(total) {
            var out = ngettext("(%(total)s total row)", " (%(total)s total rows)", total); 
            return interpolate(out, {
                total: total 
            }, true);
        },

        matching_datasets: function(offset, limit, count) {
            var out = ngettext("%(start)s-%(end)s of %(count)s matching dataset", "%(start)s-%(end)s of %(count)s matching datasets", count);
            
            return interpolate(out, {
                start: offset + 1,
                end: Math.min(offset + limit, count),
                count: count
            }, true);
        },

        total_datasets: function(total) {
            var out = ngettext("(%(total)s total dataset)", " (%(total)s total datasets)", total); 
            return interpolate(out, {
                total: total 
            }, true);
        }
    }
}
