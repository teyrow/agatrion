// Bara en inspelning i taget: pausa övriga spelare när ett spår startar.
document.addEventListener('play', function (event) {
  document.querySelectorAll('audio').forEach(function (audio) {
    if (audio !== event.target) audio.pause();
  });
}, true);
