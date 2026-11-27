const test = require("node:test");
const assert = require("node:assert/strict");
const { match, fold } = require("../../assets/nav.js");

const pages = (names) => names.map((t) => ({ t, k: "" }));

test("english ranking unchanged", () => {
  const r = match(pages(["Hidden sugars", "Sugar names", "E471"]), "sugar", 5).map((p) => p.t);
  assert.deepEqual(r, ["Sugar names", "Hidden sugars"]);
});
test("french accents fold", () => {
  assert.equal(fold("Édulcorants Œufs"), "edulcorants oeufs");
  assert.deepEqual(match(pages(["Édulcorants", "Sucre"]), "edulco", 5).map((p) => p.t), ["Édulcorants"]);
});
test("arabic article and hamza fold", () => {
  assert.deepEqual(match(pages(["السكر الخفي", "الأرز"]), "سكر", 5).map((p) => p.t), ["السكر الخفي"]);
  assert.deepEqual(match(pages(["الأرز"]), "ارز", 5).map((p) => p.t), ["الأرز"]);
});
test("e-codes still found", () => {
  assert.deepEqual(match(pages(["E471 Mono- and diglycerides"]), "e471", 5).length, 1);
});
