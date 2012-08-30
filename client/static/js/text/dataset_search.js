PANDA.text.DatasetSearch = function() {
    return {
        search_dataset: gettext("Search <strong>%(dataset)s</strong>"),
        search_placeholder: gettext("Enter a search query"),
        search: gettext("Search"),
        more_options: gettext("More search options"),
        back_to_dataset: gettext("Back to dataset details"),
        wildcards: gettext("Wildcards"),
        wildcards_help: gettext('Use an asterisk to match part of a word: <code>coff*</code> will match "coffee", "Coffer" or "coffins".'),
        exact_phrases: gettext("Exact phrases"),
        exact_phrases_help: gettext('Put phrases in quotes: <code>"Chicago Bears"</code> will not match "Chicago Panda Bears".'),
        and_or: gettext("AND/OR"),
        and_or_help: gettext('Use AND and OR to find combinations of terms: <code>homicide AND first</code> will match "first degree homicide" or "homicide, first degree", but not just "homicide".'),
        grouping: gettext("Grouping"),
        grouping_help: gettext('Group words with parantheses: <code>homicide AND (first OR 1st)</code> will match "1st degree homicide", "first degree homicide", or "homicide, first degree".'),
        alternate_names: gettext("Alternate names"),
        alternate_names_help: gettext('PANDA will attempt to match informal and alternate English first names: <code>bill</code> will match "Bill", "Billy", "William", etc. It will not match mispellings.'),
        error_title: gettext("Error importing data"),
        error_body: gettext("<p>The import failed with the following exception:</p><code>%(traceback)s</code>"),
        close: gettext("Close")
    }
}
