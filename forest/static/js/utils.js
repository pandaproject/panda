/* Serialize a form to a Javascript object. */
$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

$.fn.alert = function(type, message, close_button) {
    this.hide();
    this.removeClass("warning error success info").addClass(type);

    if (_.isUndefined(close_button)) {
        close_button = true;
    }

    if (close_button) {
        this.html("<a class=\"close\" href=\"#\">×</a>" + message);
    } else {
        this.html(message);
    }

    this.show();
    window.scrollTo(0, this.offset());
}

$(".alert-message .close").live("click", function() {
    $(this).parent().hide();
    
    return false;
});

$(".scroll-up").live("click", function() {
    window.scrollTo(0, 0);
});
