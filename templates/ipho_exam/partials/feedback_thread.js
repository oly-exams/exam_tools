function open_thread(evt){
    const a = evt.target;
    var url = "";
    if($(a).is("[href]")){
      url = $(a).attr('href');
    }else {
      url = $(a).parent().attr('href');
    }
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
  }