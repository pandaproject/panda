PANDA.text.DatasetResults = function() {
    return {
        no_query: gettext("Please enter a search query"),
        no_matching_rows: gettext("No rows matching query found in dataset <strong>%(dataset)s</strong>."),
        search_all_instead: gettext('Would you like to <a href="%(url)s">search all datasets instead</a>?'),
        subscribe: gettext("Subscribe to search results"),
        export_results: gettext("Export search results to CSV"),
        showing_after: gettext("Showing only results created or updated after <strong>%(since)s</strong>"),
        show_all: gettext("Show all results instead"),
        export_title: gettext("Are you sure you want to export this search?"),
        export_body: gettext("<p>This may take a long time to complete. You will be notified when it is finished.</p><p>Please note that changes made to the dataset during export may not be accurately reflected.</p>"),
        export_continue: gettext("Continue with export"),
        subscribe_title: gettext("Subscribe to this search?"),
        subscribe_body_email: gettext("When you click <strong>Subscribe</strong> you will begin receiving daily email notifications of new data added to PANDA that matches:"),
        subscribe_body_no_email: gettext("When you click <strong>Subscribe</strong> you will begin receiving daily notifications of new data added to PANDA that matches:"),
        subscribe_query: gettext("%(query)s in <strong>%(dataset)s</strong>"),
        subscribe_continue: gettext("Subscribe"),
        cancel: gettext("Cancel")
    }
}
