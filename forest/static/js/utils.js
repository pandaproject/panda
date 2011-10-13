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

$.fn.alert = function(type, message) {
    this.hide();
    this.removeClass("warning error success info").addClass(type);
    this.html("<a class=\"close\" href=\"#\">×</a>" + message);
    this.show();
    window.scrollTo(0, this.offset());
}

$(".alert-message .close").live("click", function() {
    $(this).parent().hide();
    
    return false;
});
