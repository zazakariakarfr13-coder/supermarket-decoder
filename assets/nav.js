/* Supermarket Decoder: ☰ menu (table of contents) on every page + site search on the homepage.
   Reads assets/search-index.json (made by scripts/make_search_index.py). Plain script, no build step. */
(function () {
  "use strict";
  var me = document.currentScript;
  if (!me) return;
  var base = new URL("..", me.src); // assets/nav.js -> site root

  var css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = new URL("assets/nav.css", base).href;
  document.head.appendChild(css);
  document.body.classList.add("has-sd-menu");

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // Ranking shared with Keep or Toss: name start > word start > anywhere in name > keyword word start.
  function match(pages, query, limit) {
    var q = query.trim().toLowerCase();
    if (!q) return [];
    var scored = [];
    pages.forEach(function (p) {
      var n = p.t.toLowerCase(), k = (p.k || "").toLowerCase(), score = -1;
      if (n.indexOf(q) === 0) score = 0;
      else if (n.split(/[^a-z0-9]+/).some(function (w) { return w.indexOf(q) === 0; })) score = 1;
      else if (n.indexOf(q) >= 0) score = 2;
      else if (k.split(/[^a-z0-9]+/).some(function (w) { return w.indexOf(q) === 0; })) score = 3;
      else if (k.indexOf(q) >= 0) score = 4;
      if (score >= 0) scored.push([score, p]);
    });
    scored.sort(function (a, b) { return a[0] - b[0] || a[1].t.localeCompare(b[1].t); });
    return scored.slice(0, limit).map(function (x) { return x[1]; });
  }

  function href(p) { return new URL(p.u, base).href; }

  function buildMenu(data) {
    var here = location.href.split("#")[0].split("?")[0].replace(/index\.html$/, "");
    var groups = data.groups.map(function (g) {
      var items = data.pages.filter(function (p) { return p.g === g; }).map(function (p) {
        var url = href(p), cur = url.replace(/index\.html$/, "") === here ? ' aria-current="page"' : "";
        return '<li><a href="' + esc(url) + '"' + cur + ">" + esc(p.t) + "</a></li>";
      }).join("");
      return items ? '<li class="sd-group"><span class="sd-h">' + esc(g) + "</span><ul>" + items + "</ul></li>" : "";
    }).join("");
    var menu = document.createElement("details");
    menu.className = "sd-menu";
    menu.innerHTML =
      '<summary aria-label="Menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>' +
      "<span>Menu</span></summary>" +
      '<nav class="sd-panel" aria-label="Site contents"><ul class="sd-list">' + groups + "</ul></nav>";
    document.body.appendChild(menu);
    document.addEventListener("click", function (e) { if (menu.open && !menu.contains(e.target)) menu.open = false; });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.open) { menu.open = false; menu.querySelector("summary").focus(); }
    });
  }

  function wireSearch(data) {
    var input = document.getElementById("sd-search");
    var list = document.getElementById("sd-results");
    var status = document.getElementById("sd-search-status");
    if (!input || !list || !status) return;
    function render() {
      var query = input.value.trim();
      var hits = match(data.pages, query, 8);
      list.innerHTML = hits.map(function (p) {
        return '<li><a href="' + esc(href(p)) + '"><span class="sd-r-t">' + esc(p.t) + '</span><span class="sd-r-g">' +
          esc(p.g) + "</span></a></li>";
      }).join("") || (query ? '<li class="sd-none">No match. Try a simpler word, like “sugar” or “E471”.</li>' : "");
      list.hidden = !query;
      input.setAttribute("aria-expanded", String(!list.hidden));
      status.textContent = !query ? "" : hits.length
        ? "Showing " + hits.length + (hits.length === 1 ? " matching page." : " matching pages.")
        : "No matching pages found.";
    }
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { var a = list.querySelector("a"); if (a) { e.preventDefault(); location.href = a.href; } }
      if (e.key === "Escape") { input.value = ""; render(); }
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".sd-search")) {
        list.hidden = true;
        input.setAttribute("aria-expanded", "false");
      }
    });
    input.addEventListener("focus", render);
  }

  fetch(new URL("assets/search-index.json", base).href)
    .then(function (r) { return r.json(); })
    .then(function (data) { buildMenu(data); wireSearch(data); })
    .catch(function () { /* menu and search are extras; the page works without them */ });
})();
