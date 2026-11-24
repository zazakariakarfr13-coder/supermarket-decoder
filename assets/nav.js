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

  /* ---------- side column on wide screens (pages with <body class="with-side">) ----------
     Space is reserved by site.css, so building it here never shifts the page. */
  function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 50); }
  function buildSide() {
    var main = document.querySelector("main");
    if (!main || !document.body.classList.contains("with-side")) return null;
    var hs = [].slice.call(main.querySelectorAll("h2"));
    var used = {};
    hs.forEach(function (h, i) {
      if (!h.id) { var id = slug(h.textContent) || "section-" + i; while (document.getElementById(id) || used[id]) id += "-" + i; h.id = id; }
      used[h.id] = 1;
    });
    var key = location.pathname.split("/").filter(Boolean).slice(-2).join("/").replace(/\.html$/, "") || "page";
    var box = "", stick = "";
    if (hs.length >= 2) {
      stick += '<nav class="sd-box sd-toc" aria-label="On this page"><div class="sd-bh">On this page</div><ol>' +
        hs.map(function (h) { return '<li><a href="#' + esc(h.id) + '">' + esc(h.textContent) + "</a></li>"; }).join("") + "</ol></nav>";
    }
    var v = main.querySelector(".verdict"), stamp = v && v.querySelector(".stamp"), num = v && v.querySelector(".num");
    if (stamp && num) {
      var vc = (v.className.match(/\b(yes|sortof|noway)\b/) || ["", ""])[1];
      box += '<div class="sd-box sd-verdict ' + vc + '"><div class="sd-bh">Verdict</div><b>' + esc(stamp.textContent) +
        "</b><span>Kitchen score " + esc(num.textContent) + "</span></div>";
    }
    stick += '<div class="sd-box sd-cta"><img src="https://public-files.gumroad.com/nbbfx502vssnurktwmojzb6uuqz2" alt="Cover of the Supermarket Decoder ebook" width="62" height="88" loading="lazy">' +
      '<div><div class="sd-bh">The guide</div><b>Read any label in 30 seconds</b><p>53-page illustrated ebook with a printable cheat-sheet.</p>' +
      '<a class="sd-btn" href="https://zakarfr.gumroad.com/l/supermarket-decoder?utm_source=github_pages&amp;utm_medium=sidebar&amp;utm_campaign=supermarket_decoder&amp;utm_content=' +
      encodeURIComponent(key) + '" target="_blank" rel="noopener">Get it · $9</a></div></div>';
    var tools = [["decoder/", "🔍", "Ingredient Decoder", "paste or scan a label"],
                 ["additives/", "🧪", "E-number lookup", "what each code does"],
                 ["factory-vs-kitchen/", "🏭", "Factory vs. Kitchen", "can you make it at home?"]];
    box += '<div class="sd-box sd-tools"><div class="sd-bh">Free tools</div><ul>' + tools.map(function (t) {
      return '<li><a href="' + esc(new URL(t[0], base).href) + '"><span aria-hidden="true">' + t[1] + "</span><span><b>" + esc(t[2]) +
        "</b><small>" + esc(t[3]) + "</small></span></a></li>";
    }).join("") + '<li><a href="https://zazakariakarfr13-coder.github.io/keep-or-toss/?utm_source=supermarket-decoder&amp;utm_medium=referral&amp;utm_campaign=sidebar">' +
      '<span aria-hidden="true">🧊</span><span><b>Keep or Toss</b><small>how long food lasts</small></span></a></li></ul></div>';
    box += '<div class="sd-box sd-rel" hidden><div class="sd-bh"></div><ul></ul></div>';
    var aside = document.createElement("aside");
    aside.className = "sd-side";
    aside.setAttribute("aria-label", "More on this site");
    aside.innerHTML = '<div class="sd-side-in">' + box + '<div class="sd-stick">' + stick + "</div></div>";
    main.appendChild(aside);
    if (hs.length >= 2 && "IntersectionObserver" in window) {
      var links = aside.querySelectorAll(".sd-toc a");
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          [].forEach.call(links, function (a) { a.classList.toggle("on", a.getAttribute("href") === "#" + e.target.id); });
        });
      }, { rootMargin: "0px 0px -70% 0px" });
      hs.forEach(function (h) { io.observe(h); });
    }
    return aside;
  }

  function fillRelated(data, aside) {
    if (!aside) return;
    var here = location.href.split("#")[0].split("?")[0].replace(/index\.html$/, "");
    var me = data.pages.filter(function (p) { return href(p).replace(/index\.html$/, "") === here; })[0];
    if (!me) return;
    var more = data.pages.filter(function (p) { return p.g === me.g && p !== me; }).slice(0, 6);
    if (!more.length) return;
    var box = aside.querySelector(".sd-rel");
    box.querySelector(".sd-bh").textContent = "More in " + me.g;
    box.querySelector("ul").innerHTML = more.map(function (p) {
      return '<li><a href="' + esc(href(p)) + '">' + esc(p.t) + "</a></li>";
    }).join("");
    box.hidden = false;
  }
  var side = buildSide();

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
      }
    });
    input.addEventListener("focus", render);
  }

  fetch(new URL("assets/search-index.json", base).href)
    .then(function (r) { return r.json(); })
    .then(function (data) { buildMenu(data); wireSearch(data); fillRelated(data, side); })
    .catch(function () { /* menu and search are extras; the page works without them */ });
})();
