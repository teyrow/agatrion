// Sökrutan på arkivsidan: filtrerar hela sidan medan man skriver.
//
// Varje spår får en söksträng av verk, sats, tonsättare, plats och datum. En
// konsert visas så länge något av dess spår matchar, och rubrikerna står kvar
// så att man ser vilken kväll man hör.
//
// Matchningen är förlåtande med flit. "Mendelson" ska hitta Mendelssohn: dels
// jämförs texten utan diakriter, dels räknas det som träff om sökordet och ett
// ord i texten delar minst sex inledande tecken. Det räddar de vanliga
// felstavningarna av långa namn utan att släppa in vad som helst.

(function () {
  "use strict";

  var PREFIX = 6;

  function normal(text) {
    return text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/[’'"”„]/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function träffar(hö, ord) {
    if (hö.indexOf(ord) !== -1) return true;
    if (ord.length < PREFIX) return false;
    // samma inledning räcker — "mendelson" mot "mendelssohn"
    return hö.split(" ").some(function (o) {
      var n = Math.min(o.length, ord.length);
      if (n < PREFIX) return false;
      var lika = 0;
      while (lika < n && o[lika] === ord[lika]) lika++;
      return lika >= PREFIX;
    });
  }

  var ruta = document.getElementById("arkivsok");
  if (!ruta) return;
  var svar = document.getElementById("arkivsvar");
  var rensa = document.getElementById("arkivrensa");

  // bygg söksträngarna en gång
  var poster = [];
  Array.prototype.forEach.call(
    document.querySelectorAll("article.recording"), function (art) {
      var rubrik = normal(art.querySelector("h3") ? art.querySelector("h3").textContent : "");
      var rader = Array.prototype.map.call(
        art.querySelectorAll("li, figure"), function (rad) {
          return { el: rad, text: rubrik + " " + normal(rad.textContent) };
        });
      poster.push({ el: art, rubrik: rubrik, rader: rader });
    });
  var avsnitt = Array.prototype.slice.call(
    document.querySelectorAll("main .section")).filter(function (s) {
      return s.querySelector("article.recording");
    });

  function filtrera() {
    var fråga = normal(ruta.value);
    var ord = fråga ? fråga.split(" ") : [];
    var träff = 0, konserter = 0;

    poster.forEach(function (p) {
      var kvar = 0;
      p.rader.forEach(function (rad) {
        var med = ord.every(function (o) { return träffar(rad.text, o); });
        rad.el.hidden = !med;
        if (med) kvar++;
      });
      p.el.hidden = kvar === 0;
      if (kvar) { konserter++; träff += kvar; }
    });
    avsnitt.forEach(function (s) {
      s.hidden = !Array.prototype.some.call(
        s.querySelectorAll("article.recording"), function (a) { return !a.hidden; });
    });

    rensa.hidden = !fråga;
    if (!fråga) {
      svar.textContent = "";
    } else if (träff === 0) {
      svar.textContent = "Ingenting matchar " + ruta.value.trim() + ".";
    } else {
      // filmklippen räknas med, så "träffar" och inte "spår"
      svar.textContent =
        träff + (träff === 1 ? " träff i " : " träffar i ") +
        konserter + (konserter === 1 ? " konsert." : " konserter.");
    }
  }

  ruta.addEventListener("input", filtrera);
  ruta.addEventListener("search", filtrera);
  rensa.addEventListener("click", function () {
    ruta.value = "";
    filtrera();
    ruta.focus();
  });
  filtrera();
})();
