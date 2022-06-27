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
button.removeClass("btn-primary")
        .removeClass("btn-default")
        .attr("data-original-title", value);

if(value == "") {
    button.addClass("btn-secondary");
} else {
    button.addClass("btn-primary");
}

$('#commentModal'+pk).modal("hide");
$('.modal-backdrop').remove();

});

$('.comment-button-tooltip').tooltip({
    show: { effect: 'slideDown', delay: 200, duration: 1000 }
});