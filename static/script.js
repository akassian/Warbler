$(document).ready(function() {
  let messageList = $("body");

  messageList.on("click", ".msg", async function(event) {
    event.preventDefault();

    let msgClicked = event.target;
    let $msgId = $(msgClicked).attr("id");
    let response = await axios.post(`/messages/${$msgId}/like`);

    $(msgClicked).toggleClass("btn-secondary btn-primary");

    let likeCount = $("#like-count");
    if (likeCount) {
      let currentCount = parseInt($(likeCount).text());
      if ($(msgClicked).hasClass("btn-primary")) {
        currentCount++; // after the toggle already happened
      } else {
        currentCount--;
      }
      $(likeCount).text(currentCount);
    }
  });

  let newWarbleSubmit = $("#new-warble-submit");
  newWarbleSubmit.on("click", async function(event) {
    // event.preventDefault();
    let warble = $("#new-warble-text").val();
    console.log(warble);
    let msg = await axios.post("/messages/new", (data = { text: warble }));
    let newMsg = generateMsgHTML(msg);
    console.log(newMsg);
    $("#messages").prepend(newMsg);
    $("#new-warble-text").val("");
    $(".modal").modal("toggle");
  });

  function generateMsgHTML(msg) {
    let newMsg = `
    <li class="list-group-item">
    <!-- <a href="/messages/${msg.data.id}" class="message-link" /> -->
    <a href="/users/${msg.data.user_id}">
      <img src="${msg.data.user_image_url}" alt="" class="timeline-image" />
    </a>
    <div class="message-area">
      <a href="/users/${msg.data.user_id}">@${msg.data.user_username}</a>
      <span class="text-muted"
        >${msg.data.timestamp}</span
      >
      <p>${msg.data.text}</p>
    </div>
  </li>
  `;
    return newMsg;
  }
});
