// Lists every English string the decoder can show, so the French and Arabic text files can be checked.
// Usage: node scripts/decoder_strings.js            -> JSON {keys: [...], data: [...]} on stdout
//        node scripts/decoder_strings.js check fr   -> exit 1 if assets/decoder-text.fr.js misses a key or changes a number
const fs = require("fs");
const vm = require("vm");
const path = require("path");
const ROOT = path.join(__dirname, "..");

function stubElement() {
  return new Proxy(function () {}, {
    get: (t, k) => (k === "addEventListener" || k === "appendChild" || k === "focus" || k === "scrollIntoView" || k === "setAttribute") ? () => {} :
      (k === "style" || k === "classList" || k === "dataset") ? stubElement() : (k === "value" || k === "textContent" || k === "innerHTML") ? "" : undefined,
    set: () => true,
  });
}
function load() {
  const win = {};
  const ctx = { window: win, document: { getElementById: stubElement, querySelectorAll: () => [], querySelector: () => null,
    createElement: stubElement, createTextNode: stubElement, documentElement: { lang: "en" } },
    location: { hash: "", href: "", pathname: "/" }, history: { replaceState() {} }, navigator: {}, console };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT, "assets/decoder.js"), "utf8"), ctx);
  return win.SD_DECODER_DATA;
}
function literalKeys() {
  const keys = new Set();
  for (const f of ["assets/decoder.js", "assets/decoder-scan.js"]) {
    const src = fs.readFileSync(path.join(ROOT, f), "utf8");
    for (const m of src.matchAll(/\bL\("((?:[^"\\]|\\.)*)"/g)) keys.add(JSON.parse('"' + m[1] + '"'));
  }
  return [...keys];
}
function dataStrings(D) {
  const out = new Set();
  Object.values(D.F).forEach((v) => out.add(v));
  Object.values(D.E).forEach((e) => { out.add(e[0]); if (e[2]) out.add(e[2]); });
  D.DICT.forEach((d) => { if (d.t) out.add(d.t); if (d.d) out.add(d.d); });
  D.CLASSES.forEach((c) => { out.add(c.fn); out.add(c.why); });
  D.ALLERGENS.forEach((a) => out.add(a[0]));
  return [...out];
}
function tokens(s) {
  const c = {};
  s = s.replace(/\{\w+\}/g, (m) => { c[m] = (c[m] || 0) + 1; return " "; });
  s = s.replace(/(?<![A-Za-z0-9])E ?(\d{3,4}[a-z]?)(?![A-Za-z0-9])/g, (m, x) => { c["E" + x] = (c["E" + x] || 0) + 1; return " "; });
  for (const m of s.matchAll(/\d+(?:[.,]\d+)?/g)) { const k = m[0].replace(",", "."); c[k] = (c[k] || 0) + 1; }
  return JSON.stringify(Object.keys(c).sort().map((k) => [k, c[k]]));
}
const D = load();
function fnv(str) { let h = 0x811c9dc5; for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(16).padStart(8, "0"); }
const keys = literalKeys(), data = dataStrings(D);
if (process.argv[2] === "check") {
  const lang = process.argv[3];
  const w = {};
  for (const f of [`assets/decoder-text.${lang}.js`, `assets/decoder-data.${lang}.js`]) {
    if (fs.existsSync(path.join(ROOT, f))) vm.runInNewContext(fs.readFileSync(path.join(ROOT, f), "utf8"), { window: w });
  }
  const X = w.SD_DECODER_TEXT, T = X.text, DATA = X.data || {};
  let bad = 0;
  for (const k of keys) {
    if (!(k in T)) { console.log("missing:", k.slice(0, 90)); bad++; continue; }
    if (tokens(k) !== tokens(T[k])) { console.log("numbers differ:", k.slice(0, 70), "|", T[k].slice(0, 70)); bad++; }
  }
  const wanted = new Set(data.map(fnv));
  for (const k of data) {
    const h = fnv(k);
    if (!(h in DATA)) { if (process.argv[4] !== "--keys-only") console.log("missing data", h, k.slice(0, 80)); bad++; continue; }
    if (lang !== "ar-names" && tokens(k) !== tokens(DATA[h])) { console.log("numbers differ:", h, k.slice(0, 60), "|", DATA[h].slice(0, 60)); bad++; }
  }
  for (const h of Object.keys(DATA)) if (!wanted.has(h)) { console.log("unknown data key", h); bad++; }
  for (const s of Object.keys(X.samples || {})) if (!(s in D.SAMPLES)) { console.log("unknown sample", s); bad++; }
  console.log(`${lang}: ${keys.length + data.length - bad} ok, ${bad} problems`);
  process.exit(bad ? 1 : 0);
} else if (process.argv[2] === "names") {
  // hashes of the E-number chemical names (Arabic pages show them in their French form, as on Moroccan labels)
  const names = new Set(Object.values(D.E).map((e) => e[0]));
  [...names].forEach((n) => console.log(fnv(n)));
} else if (process.argv[2] === "list") {
  // work list for translators: hash | English, in the order the data appears
  data.forEach((k) => console.log(fnv(k) + " | " + k));
} else {
  process.stdout.write(JSON.stringify({ keys, data }, null, 1));
}
