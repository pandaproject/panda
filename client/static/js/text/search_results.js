PANDA.text.SearchResults = function() {
    return {
        enter_query: gettext("Please enter a search query."),
        no_results: gettext("No rows matching query found in any dataset."),
        subscribe: gettext("Subscribe to search results"),
        export_results: gettext("Export search results to CSV files"),
        showing_after: gettext("Showing only results created or updated after <strong>%(since)s</strong>."),
        show_all: gettext("Show all results instead"),
        more_results: gettext("View more results from this dataset"),

        export_title: gettext("Are you sure you want to export this search?"),
        export_body: gettext("<p>This may take a long time to complete. You will be notified when it is finished.</p><p>Please note that changes made to the data during export may not be accurately reflected.</p>"),
        export_cancel: gettext("Cancel"),
        export_continue: gettext("Continue with export"),

        subscribe_title: gettext("Subscribe to this search?"),
        subscribe_body_email: gettext("When you click <strong>Subscribe</strong> you will begin receiving daily email notifications of new data added to PANDA that matches your search."),
        subscribe_body_no_email: gettext("When you click <strong>Subscribe</strong> you will begin receiving daily notifications of new data added to PANDA that matches your search."),
        subscribe_cancel: gettext("Cancel"),
        subscribe_continue: gettext("Subscribe")
    }
}
