// Bara en inspelning i taget: pausa övriga spelare när ett spår startar.
document.addEventListener('play', function (event) {
  document.querySelectorAll('audio').forEach(function (audio) {
    if (audio !== event.target) audio.pause();
  });
}, true);

// Ladda YouTube först när besökaren klickar, så inga tredjepartsanrop sker vid sidladdning.
document.querySelectorAll('.video-embed[data-youtube]').forEach(function (button) {
  button.addEventListener('click', function () {
    var iframe = document.createElement('iframe');
    iframe.src = 'https://www.youtube-nocookie.com/embed/' + button.dataset.youtube + '?autoplay=1';
    iframe.title = button.dataset.title || 'Video';
    iframe.allow = 'accelerometer; autoplay; encrypted-media; picture-in-picture';
    iframe.allowFullscreen = true;
    button.replaceChildren(iframe);
  }, { once: true });
});
