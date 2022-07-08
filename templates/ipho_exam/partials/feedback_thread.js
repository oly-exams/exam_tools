$('#feedback-thread-modal').on('show.bs.modal', function (event) {
  {% include "ipho_exam/partials/stackable_modal_fix.js" %}
  var button = $(event.relatedTarget);
  var url = button.attr("url");
  
  $.ajax({
    url: url,
    data: 'GET',
  }).done(function( data ) {
    $('#thread-area').html(data.text);
    
    $('#thread-area .comment-submit').on("click", function(evt) {
      var text = $('#thread-area .comment-text').first()[0].value;
      $.ajax({
        url: url,
        type: 'POST',
        data: {text: text},
      }).done(function(data){
        $('#thread-area .comment-area').append(data.new_comment);
        $('#thread-area .comment-text').first()[0].value = "";
      });
    });
  }); 
});