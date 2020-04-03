$( document ).ready(function() {

  let messageList = $( "body" );

  messageList.on( "click", ".msg", async function( event ) {
    event.preventDefault();
    
    let msgClicked = event.target;
    let $msgId = $(msgClicked).attr('id');
    let response = await axios.post(`/messages/${$msgId}/like`);

    $(msgClicked).toggleClass( 'btn-secondary btn-primary' );

    let likeCount = $("#like-count");
    if (likeCount) {
      let currentCount = parseInt($(likeCount).text());
      // console.log($(likeCount).text())
      if ($(msgClicked).hasClass( 'btn-primary' )) {
        currentCount++;  // after the toggle already happened
      } else {
        currentCount--;
      }
      $(likeCount).text( currentCount );
    }
  });
});
