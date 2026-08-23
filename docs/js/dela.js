// Dela sidan med systemets egen delningsmeny där den finns, annars kopiera länken.
// Knappen är dold tills skriptet kört, så den aldrig ligger död för den utan JavaScript.
document.querySelectorAll('button.dela').forEach(function (knapp) {
  knapp.hidden = false;
  knapp.addEventListener('click', async function () {
    var data = {
      title: document.title,
      text: (document.querySelector('meta[name="description"]') || {}).content || '',
      url: location.href
    };
    try {
      if (navigator.share) {
        await navigator.share(data);
        return;
      }
      await navigator.clipboard.writeText(location.href);
      var original = knapp.textContent;
      knapp.textContent = 'Länken är kopierad';
      setTimeout(function () { knapp.textContent = original; }, 2500);
    } catch (e) {
      // Avbruten delning är inget fel — låt knappen vara som den är.
    }
  });
});
