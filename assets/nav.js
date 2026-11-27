/* Supermarket Decoder: ☰ menu (table of contents) on every page + site search on the homepage.
   Reads assets/search-index.json (or .fr.json / .ar.json, made by scripts/make_search_index.py) and speaks
   the page's language (<html lang>). Plain script, no build step. */
(function () {
  "use strict";

  // Lowercase, drop French accents and Arabic short vowels, even out Arabic letter forms, and drop a
  // leading "ال" (the), so "edulco" finds "Édulcorants" and "سكر" finds "السكر".
  function fold(s) {
    return String(s).toLowerCase()
      .replace(/œ/g, "oe").replace(/æ/g, "ae")
      .normalize("NFD").replace(/[̀-ͯ]/g, "").normalize("NFC")
      .replace(/[ً-ْٰـ]/g, "")
      .replace(/[أإآٱ]/g, "ا").replace(/ة/g, "ه").replace(/ى/g, "ي")
      .replace(/(^|[^\p{L}\p{N}])ال(?=\p{L}{2})/gu, "$1");
  }
  function words(s) { return s.split(/[^\p{L}\p{N}]+/u); }

  // Ranking shared with Keep or Toss: name start > word start > anywhere in name > keyword word start.
  function match(pages, query, limit) {
    var q = fold(query.trim());
    if (!q) return [];
    var scored = [];
    pages.forEach(function (p) {
      var n = fold(p.t), k = fold(p.k || ""), score = -1;
      if (n.indexOf(q) === 0) score = 0;
      else if (words(n).some(function (w) { return w.indexOf(q) === 0; })) score = 1;
      else if (n.indexOf(q) >= 0) score = 2;
      else if (words(k).some(function (w) { return w.indexOf(q) === 0; })) score = 3;
      else if (k.indexOf(q) >= 0) score = 4;
      if (score >= 0) scored.push([score, p]);
    });
    scored.sort(function (a, b) { return a[0] - b[0] || a[1].t.localeCompare(b[1].t); });
    return scored.slice(0, limit).map(function (x) { return x[1]; });
  }

  if (typeof module !== "undefined" && module.exports) module.exports = { match: match, fold: fold };
  if (typeof document === "undefined") return;

  var me = document.currentScript;
  if (!me) return;
  var base = new URL("..", me.src); // assets/nav.js -> site root
  var lang = (document.documentElement.lang || "en").slice(0, 2);
  if (lang !== "fr" && lang !== "ar") lang = "en";
  var pre = lang === "en" ? "" : lang + "/";

  var T = {
    en: { menu: "Menu", contents: "Site contents", onPage: "On this page", verdict: "Verdict", score: "Kitchen score",
          guide: "The guide", guideTitle: "Read any label in 30 seconds", guideText: "53-page illustrated ebook with a printable cheat-sheet.",
          buy: "Get it · $9", guideLang: "", tools: "Free tools", more: "More in ", side: "More on this site",
          decoder: ["Ingredient Decoder", "paste or scan a label"], additives: ["E-number lookup", "what each code does"],
          fvk: ["Factory vs. Kitchen", "can you make it at home?"], kot: ["Keep or Toss", "how long food lasts"],
          noMatch: "No match. Try a simpler word, like “sugar” or “E471”.", showing1: "Showing 1 matching page.",
          showingN: "Showing {n} matching pages.", none: "No matching pages found.", cover: "Cover of the Supermarket Decoder ebook" },
    fr: { menu: "Menu", contents: "Contenu du site", onPage: "Sur cette page", verdict: "Verdict", score: "Score cuisine",
          guide: "Le guide", guideTitle: "Lire une étiquette en 30 secondes", guideText: "Ebook illustré de 53 pages avec une fiche mémo à imprimer.",
          buy: "Le prendre · 9 $", guideLang: "En anglais.", tools: "Outils gratuits", more: "Plus dans : ", side: "Plus sur ce site",
          decoder: ["Décodeur d’ingrédients", "collez ou scannez une étiquette"], additives: ["Fiches additifs (E)", "à quoi sert chaque code"],
          fvk: ["Usine ou cuisine", "peut-on le faire maison ?"], kot: ["Keep or Toss", "combien de temps se garde un aliment"],
          noMatch: "Aucun résultat. Essayez un mot plus simple, comme « sucre » ou « E471 ».", showing1: "1 page trouvée.",
          showingN: "{n} pages trouvées.", none: "Aucune page trouvée.", cover: "Couverture de l’ebook Supermarket Decoder" },
    ar: { menu: "القائمة", contents: "محتويات الموقع", onPage: "في هذه الصفحة", verdict: "الحكم", score: "نقاط المطبخ",
          guide: "الدليل", guideTitle: "اقرأ أي ملصق في 30 ثانية", guideText: "كتاب إلكتروني مصوّر من 53 صفحة مع ورقة ملخّص للطباعة.",
          buy: "احصل عليه · 9 $", guideLang: "باللغة الإنجليزية.", tools: "أدوات مجانية", more: "المزيد في: ", side: "المزيد في هذا الموقع",
          decoder: ["مفكّك المكوّنات", "الصق ملصقًا أو امسحه"], additives: ["دليل الإضافات (E)", "وظيفة كل رمز"],
          fvk: ["المصنع أم المطبخ", "هل يمكن صنعه في البيت؟"], kot: ["Keep or Toss", "كم يدوم الطعام"],
          noMatch: "لا نتيجة. جرّب كلمة أبسط، مثل «سكر» أو «E471».", showing1: "صفحة واحدة مطابقة.",
          showingN: "عدد الصفحات المطابقة: {n}.", none: "لا توجد صفحات مطابقة.", cover: "غلاف كتاب Supermarket Decoder الإلكتروني" }
  }[lang];

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
      stick += '<nav class="sd-box sd-toc" aria-label="' + esc(T.onPage) + '"><div class="sd-bh">' + esc(T.onPage) + '</div><ol>' +
        hs.map(function (h) { return '<li><a href="#' + esc(h.id) + '">' + esc(h.textContent) + "</a></li>"; }).join("") + "</ol></nav>";
    }
    var v = main.querySelector(".verdict"), stamp = v && v.querySelector(".stamp"), num = v && v.querySelector(".num");
    if (stamp && num) {
      var vc = (v.className.match(/\b(yes|sortof|noway)\b/) || ["", ""])[1];
      box += '<div class="sd-box sd-verdict ' + vc + '"><div class="sd-bh">' + esc(T.verdict) + '</div><b>' + esc(stamp.textContent) +
        "</b><span>" + esc(T.score) + " " + esc(num.textContent) + "</span></div>";
    }
    stick += '<div class="sd-box sd-cta"><img src="https://public-files.gumroad.com/nbbfx502vssnurktwmojzb6uuqz2" alt="' + esc(T.cover) + '" width="62" height="88" loading="lazy">' +
      '<div><div class="sd-bh">' + esc(T.guide) + '</div><b>' + esc(T.guideTitle) + '</b><p>' + esc(T.guideText) +
      (T.guideLang ? ' <span class="guide-lang">' + esc(T.guideLang) + '</span>' : '') + '</p>' +
      '<a class="sd-btn" href="https://zakarfr.gumroad.com/l/supermarket-decoder?utm_source=github_pages&amp;utm_medium=sidebar&amp;utm_campaign=supermarket_decoder&amp;utm_content=' +
      encodeURIComponent(key + (lang === "en" ? "" : "-" + lang)) + '" target="_blank" rel="noopener">' + esc(T.buy) + '</a></div></div>';
    var tools = [["decoder/", "🔍", T.decoder[0], T.decoder[1]],
                 ["additives/", "🧪", T.additives[0], T.additives[1]],
                 ["factory-vs-kitchen/", "🏭", T.fvk[0], T.fvk[1]]];
    box += '<div class="sd-box sd-tools"><div class="sd-bh">' + esc(T.tools) + '</div><ul>' + tools.map(function (t) {
      return '<li><a href="' + esc(new URL(pre + t[0], base).href) + '"><span aria-hidden="true">' + t[1] + "</span><span><b>" + esc(t[2]) +
        "</b><small>" + esc(t[3]) + "</small></span></a></li>";
    }).join("") + '<li><a href="https://zazakariakarfr13-coder.github.io/keep-or-toss/' + pre + '?utm_source=supermarket-decoder&amp;utm_medium=referral&amp;utm_campaign=sidebar">' +
      '<span aria-hidden="true">🧊</span><span><b>' + esc(T.kot[0]) + '</b><small>' + esc(T.kot[1]) + '</small></span></a></li></ul></div>';
    box += '<div class="sd-box sd-rel" hidden><div class="sd-bh"></div><ul></ul></div>';
    var aside = document.createElement("aside");
    aside.className = "sd-side";
    aside.setAttribute("aria-label", T.side);
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
    box.querySelector(".sd-bh").textContent = T.more + me.g;
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
      '<summary aria-label="' + esc(T.menu) + '"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>' +
      "<span>" + esc(T.menu) + "</span></summary>" +
      '<nav class="sd-panel" aria-label="' + esc(T.contents) + '"><ul class="sd-list">' + groups + "</ul></nav>";
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
      }).join("") || (query ? '<li class="sd-none">' + esc(T.noMatch) + '</li>' : "");
      list.hidden = !query;
      status.textContent = !query ? "" : hits.length
        ? (hits.length === 1 ? T.showing1 : T.showingN.replace("{n}", hits.length))
        : T.none;
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

  fetch(new URL(lang === "en" ? "assets/search-index.json" : "assets/search-index." + lang + ".json", base).href)
    .then(function (r) { return r.json(); })
    .then(function (data) { buildMenu(data); wireSearch(data); fillRelated(data, side); })
    .catch(function () { /* menu and search are extras; the page works without them */ });
})();
