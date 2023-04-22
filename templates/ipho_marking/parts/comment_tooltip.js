$('.modal').on('shown.bs.modal', function () {
    $(".modal-body textarea", this).focus();
})

$(".modal-close").on("click", function() {

pk = this.attributes.pk.value
button = $("#commentButton"+pk);
input = $("#commentModal"+pk+" .modal-body textarea").first()[0]
input.innerHTML = input.value;
value = input.value;
console.log(value);
button.attr("data-original-title", value);
icon = $("i", button)
icon.removeClass("fa-comment-o").removeClass("fa-comment")

if(value == "") {
    icon.addClass("fa-comment-o");
} else {
    icon.addClass("fa-comment");
}

$('#commentModal'+pk).modal("hide");
$('.modal-backdrop').remove();

});

$('.comment-button-tooltip').tooltip({
    show: { effect: 'slideDown', delay: 200, duration: 1000 }
});