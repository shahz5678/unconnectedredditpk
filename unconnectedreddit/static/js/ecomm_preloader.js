$(document).ready(function() {
    $(document).on("click", ".UploadBtn", function(event) {
        $(".p").each(function(file) {
            if  ($(this).val()) {
                $(".loader").show();
                $(".spinner").show();
                $("#overlay").show();
            }
        })
    });
});
