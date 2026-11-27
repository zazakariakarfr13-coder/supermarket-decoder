// Paste into the browser console on /decoder/ (English). Prints "ALL SAME" when the English decoder still
// produces exactly the output recorded on 2026-11-27, before the decoder was made multilingual.
(function () {
  const lists = {
    bar: null, bread: null, cola: null, yog: null,
    fr1: "Farine de blé, sucre, huile de palme, sirop de glucose-fructose, émulsifiant : lécithine de soja (E322), poudre à lever : E500, sel, arôme, colorant : E150d.",
    fr2: "Eau, sucre, jus d'orange à base de concentré (5%), acidifiant : acide citrique, conservateurs : sorbate de potassium, benzoate de sodium, édulcorant : sucralose.",
    en1: "Pork (87%), water, salt, dextrose, stabiliser: sodium triphosphate, antioxidant: sodium ascorbate, preservative: sodium nitrite. May contain traces of milk.",
    en2: "Sugar, glucose syrup, gelatine, citric acid, flavourings, colours: Red 40, Yellow 5, Blue 1, carnauba wax. Contains: milk.",
    en3: "Wheat flour, water, yeast, salt, emulsifiers (E471, E472e), flour treatment agent (ascorbic acid), maltodextrin, xyz-unknownium",
    en4: "Water, rapeseed oil, spirit vinegar, sugar, egg yolk, salt, mustard (water, mustard seed, vinegar), stabiliser: xanthan gum, E999z",
  };
  const want = { bar: "df55e607:4115", bread: "c8c24191:4366", cola: "99e10c04:2535", yog: "eeaa072f:3342", fr1: "62150e51:4305",
    fr2: "a4c19955:2971", en1: "67ef5fea:3045", en2: "d29e1053:4246", en3: "217bba58:3751", en4: "95fc0800:3575" };
  const h = (s) => { let x = 0; for (const c of s) x = (x * 31 + c.codePointAt(0)) >>> 0; return x.toString(16) + ":" + s.length; };
  const out = {};
  for (const [k, v] of Object.entries(lists)) {
    if (v === null) document.querySelector('[data-sample="' + k + '"]').click();
    else { document.getElementById("list").value = v; document.getElementById("go").click(); }
    out[k] = h(document.getElementById("results").innerText);
  }
  const bad = Object.keys(want).filter((k) => want[k] !== out[k]);
  return bad.length ? "DIFFERENT: " + bad.join(", ") : "ALL SAME";
})();
