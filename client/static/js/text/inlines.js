PANDA.text.Inlines = function() {
    /* Text blobs for inlines that are reused in multiple views. */
    return {
        // inline_pager.jst
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

            console.log(out);
            
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
        },

        // inline_upload_item.jst
        uploaded_by: gettext("uploaded by %(user)s"),
        uploaded_on: gettext("Uploaded %(when)s"),
        edit_title: gettext("Edit title"),
        click_to_delete: gettext("Click to delete"),

        // inline_advanced_search_tooltip.jst
        tip_text: gettext('<ul><li>Use an asterisk to match part of a word: <code>coff*</code> will match &quot;coffee&quot;, &quot;Coffer&quot; or &quot;coffins&quot;.</li><li>Put phrases in quotes: <code>&quot;Chicago Bears&quot;</code> will not match &quot;Chicago Panda Bears&quot;.</li><li>Use AND and OR to find combinations of terms: <code>homicide AND first</code> will match &quot;first degree homicide&quot; or &quot;homicide, first degree&quot;, but not just &quot;homicide&quot;.</li><li>Group words with parantheses: <code>homicide AND (first OR 1st)</code> will match &quot;1st degree homicide&quot;, &quot;first degree homicide&quot;, or &quot;homicide, first degree&quot;.</li><li>PANDA will attempt to match informal and alternate English first names: <code>bill</code> will match &quot;Bill&quot;, &quot;Billy&quot;, &quot;William&quot;, etc. It will not match mispellings.</li></ul>'),
        tip_title: gettext("Advanced searching"),
        advanced: gettext("Advanced")
    }
}
