
// Show modal before tournament game
function announceGame(round, message) {
  let messageModal =
      new bootstrap.Modal(document.getElementById('messageModal'));
  messageModal.show();
  document.getElementById('messageModalLabel').innerText = round;
  document.getElementById('messageContent').innerText = message;
  document.getElementById('messageContent').classList.remove('text-end');
  document.getElementById('messageContent').classList.add('text-center');
}
// Show message modal
function displayMessageInModal(message) {
  if (message) {
    console.log('displayMessageInModal > message: ', message);
    let messageModal =
        new bootstrap.Modal(document.getElementById('messageModal'));
    messageModal.show();
    document.getElementById('messageModalLabel').innerText = notificationMsg;
    document.getElementById('messageContent').innerText = message;
    document.getElementById('messageContent').classList.remove('text-center');
    document.getElementById('messageContent').classList.add('text-end');
  }
}

// Get value of a cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
