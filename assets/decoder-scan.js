/* Barcode / QR scan -> Open Food Facts lookup -> fills the ingredient box and decodes.
   Camera frames are read on the device; only the product number is sent to Open Food Facts. */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var ZXING = "https://cdn.jsdelivr.net/npm/@zxing/library@0.21.3/umd/index.min.js";
  var OFF = "https://world.openfoodfacts.org/api/v2/product/";
  var FIELDS = "product_name,product_name_en,brands,ingredients_text,ingredients_text_en,ingredients_text_fr,image_front_small_url";
  var stream = null, timer = null, zxReader = null, busy = false, starting = false, scanRun = 0, detecting = false;

  function say(html) { $("smsg").innerHTML = html; }
  // Words come from assets/decoder-text.<lang>.js (window.SD_DECODER_TEXT), keyed by the English text; English is built in.
  var TX = window.SD_DECODER_TEXT || null;
  function L(en, v) {
    var t = (TX && TX.ui && TX.ui[en]) || en;
    return v ? t.replace(/\{(\w+)\}/g, function (m, k) { return k in v ? v[k] : m; }) : t;
  }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  /* ---------- turning a scanned value into a product number ---------- */
  function checkDigitOk(d) {
    var sum = 0, n = d.length;
    for (var i = 0; i < n - 1; i++) sum += +d[i] * ((n - 1 - i) % 2 ? 3 : 1);
    return (10 - sum % 10) % 10 === +d[n - 1];
  }
  function isUpceFormat(format) {
    var zxingUpce = window.ZXing && window.ZXing.BarcodeFormat && window.ZXing.BarcodeFormat.UPC_E;
    return format === "upc_e" || format === "UPC_E" || (zxingUpce !== undefined && format === zxingUpce);
  }
  function expandUpce(s) {
    if (!/^[01]\d{6}\d$/.test(s)) return null;
    var ns = s[0], x1 = s[1], x2 = s[2], x3 = s[3], x4 = s[4], x5 = s[5], x6 = s[6], cd = s[7];
    var body;
    if (+x6 <= 2) body = ns + x1 + x2 + x6 + "0000" + x3 + x4 + x5;
    else if (+x6 === 3) body = ns + x1 + x2 + x3 + "00000" + x4 + x5;
    else if (+x6 === 4) body = ns + x1 + x2 + x3 + x4 + "00000" + x5;
    else body = ns + x1 + x2 + x3 + x4 + x5 + "0000" + x6;
    var expanded = body + cd;
    return checkDigitOk(expanded) ? expanded : null;
  }
  function toGtin(raw, format) {
    var s = String(raw).trim(), m;
    // UPC-E is a zero-suppressed GTIN-12; expand it before querying Open Food Facts.
    if (isUpceFormat(format)) return expandUpce(s);
    if (/^\d{8,14}$/.test(s)) return s;
    // GS1 Digital Link QR: https://brand.example/01/03017620422003/...
    m = s.match(/\/01\/(\d{8,14})(?:[\/?#]|$)/); if (m) return m[1];
    // GS1 element string: (01)03017620422003...  or  0103017620422003...
    m = s.replace(/[()]/g, "").match(/^01(\d{14})/); if (m) return m[1];
    return null;
  }
  function tidy(g) { return g.length === 14 && g[0] === "0" ? g.slice(1) : g; }

  function handle(raw, format) {
    var g = toGtin(raw, format);
    if (g) return lookup(tidy(g));
    if (isUpceFormat(format)) {
      say(L("This UPC-E barcode could not be verified. Try scanning it again or type the full number printed on the pack."));
      return;
    }
    if (/^https?:\/\//i.test(String(raw).trim())) {
      say(L("This QR code is a link, not a product number: {link}. Check the address before opening it. To get the ingredients, scan the striped barcode or a GS1 product QR code instead.",
          { link: "<a href=\"" + esc(raw.trim()) + "\" target=\"_blank\" rel=\"noopener noreferrer nofollow\">" + esc(raw.trim().slice(0, 70)) + "</a>" }));
    } else {
      say(L("That code doesn't look like a product barcode. Try the striped barcode on the pack, or type the numbers printed under it."));
    }
  }

  /* ---------- Open Food Facts ---------- */
  function lookup(code) {
    if (busy) return; busy = true;
    $("code").value = code;
    if (!checkDigitOk(code)) say(L("Looking up {code}… (the last digit looks off, so double-check the number if nothing is found)", { code: esc(code) }));
    else say(L("Looking up {code}…", { code: esc(code) }));
    var ctl = window.AbortController ? new AbortController() : null;
    var to = setTimeout(function () { if (ctl) ctl.abort(); }, 12000);
    var requestOptions = { credentials: "omit", referrerPolicy: "no-referrer" };
    if (ctl) requestOptions.signal = ctl.signal;
    fetch(OFF + encodeURIComponent(code) + ".json?fields=" + FIELDS, requestOptions)
      .then(function (r) { if (r.status === 404) return { status: 0 }; if (!r.ok) throw new Error("http " + r.status); return r.json(); })
      .then(function (d) { show(code, d); })
      .catch(function () {
        say(L("Couldn't reach the product database just now. Check your connection and try again, or type the ingredients from the pack below."));
      })
      .then(function () { clearTimeout(to); busy = false; });
  }
  function show(code, d) {
    var offUrl = "https://world.openfoodfacts.org/product/" + encodeURIComponent(code);
    if (!d || d.status !== 1 || !d.product) {
      $("prod").hidden = true;
      say(L("No product with barcode {code} in Open Food Facts yet. Type or paste the ingredients from the pack below. You can also {addlink}add it to Open Food Facts{end} so the next person finds it.",
          { code: esc(code), addlink: "<a href=\"https://world.openfoodfacts.org/cgi/product.pl?type=add&code=" + encodeURIComponent(code) + "\" target=\"_blank\" rel=\"noopener\">", end: "</a>" }));
      return;
    }
    var p = d.product;
    var name = (TX && TX.lang === "fr" && p.product_name_fr) || p.product_name_en || p.product_name || L("Product {code}", { code: code });
    // volunteers sometimes enter only part of a list in one language: take the most complete one (English wins ties)
    var cands = (TX && TX.lang !== "en" ? [["fr", p.ingredients_text_fr], ["", p.ingredients_text], ["en", p.ingredients_text_en]]
      : [["en", p.ingredients_text_en], ["", p.ingredients_text], ["fr", p.ingredients_text_fr]])
      .filter(function (c) { return c[1] && c[1].trim(); })
      .map(function (c) { return [c[0], c[1].replace(/_/g, "").trim(), c[1].split(/[,;]/).length]; });
    var best = cands.reduce(function (a, c) { return !a || c[2] > a[2] ? c : a; }, null);
    var ings = best ? best[1] : "";
    var inFrench = (!TX || TX.lang === "en") && best && best[0] === "fr" && best[1] !== (p.ingredients_text_en || "").trim();
    $("prodName").textContent = name;
    $("prodMeta").innerHTML = (p.brands ? esc(p.brands.split(",")[0]) + " · " : "") + L("barcode {code}", { code: esc(code) }) +
      "<br>" + L("Ingredients from {offlink}Open Food Facts{end}, entered by volunteers. Check them against the pack.",
        { offlink: "<a href=\"" + offUrl + "\" target=\"_blank\" rel=\"noopener noreferrer\">", end: "</a>" });
    if (p.image_front_small_url && /^https:\/\//.test(p.image_front_small_url)) { $("prodImg").src = p.image_front_small_url; $("prodImg").alt = name; $("prodImg").hidden = false; }
    else $("prodImg").hidden = true;
    $("prod").hidden = false;
    if (!ings) {
      say(L("Found {name}, but nobody has added its ingredient list yet. Type it from the pack below, or {offlink}add it on Open Food Facts{end}.",
          { name: "<b>" + esc(name) + "</b>", offlink: "<a href=\"" + offUrl + "\" target=\"_blank\" rel=\"noopener noreferrer\">", end: "</a>" }));
      $("list").value = ""; $("list").focus();
      return;
    }
    say(L("✅ Found {name}. Its ingredients are decoded below.", { name: "<b>" + esc(name) + "</b>" }) +
        (inFrench ? " (The French-language entry had the most listed items in the database; it may still be incomplete or outdated, so check it against the pack.)" : ""));
    $("list").value = ings;
    $("go").click();
  }

  /* ---------- camera ---------- */
  function loadZxing() {
    return new Promise(function (ok, bad) {
      if (window.ZXing) return ok();
      var s = document.createElement("script");
      s.referrerPolicy = "no-referrer";
      s.src = ZXING; s.onload = ok; s.onerror = bad; document.head.appendChild(s);
    });
  }
  function nativeDetector() {
    if (!("BarcodeDetector" in window)) return Promise.resolve(null);
    return BarcodeDetector.getSupportedFormats().then(function (f) {
      var want = ["ean_13", "ean_8", "upc_a", "upc_e", "qr_code"].filter(function (x) { return f.indexOf(x) > -1; });
      return want.indexOf("ean_13") > -1 ? new BarcodeDetector({ formats: want }) : null;
    }).catch(function () { return null; });
  }
  function stop() {
    scanRun++;
    starting = false;
    detecting = false;
    if (timer) { clearInterval(timer); timer = null; }
    if (zxReader) { try { zxReader.reset(); } catch (e) {} zxReader = null; }
    if (stream) { stream.getTracks().forEach(function (t) { t.stop(); }); stream = null; }
    var video = $("camVideo");
    if (video) { try { video.pause(); } catch (e) {} video.srcObject = null; }
    $("cam").hidden = true;
  }
  function found(value, format) { stop(); if (navigator.vibrate) navigator.vibrate(60); handle(value, format); }

  function start() {
    if (starting || stream || zxReader) return;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      say(L("This browser can't open the camera. Use <b>Use a photo</b>, or type the barcode number.")); return;
    }
    starting = true;
    var run = ++scanRun;
    say(L("Opening the camera…"));
    var video = $("camVideo");
    nativeDetector().then(function (det) {
      if (run !== scanRun) return;
      if (det) {
        return navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false }).then(function (s) {
          if (run !== scanRun) { s.getTracks().forEach(function (t) { t.stop(); }); return; }
          stream = s; starting = false; video.srcObject = s; $("cam").hidden = false; say(L("Camera ready. Hold the barcode inside the highlighted box."));
          return video.play().then(function () {
            if (run !== scanRun) return;
            timer = setInterval(function () {
              if (detecting || video.readyState < 2) return;
              detecting = true;
              det.detect(video).then(function (codes) {
                if (run === scanRun && codes.length) found(codes[0].rawValue, codes[0].format);
              }).catch(function () {}).then(function () { detecting = false; });
            }, 250);
          });
        });
      }
      return loadZxing().then(function () {
        if (run !== scanRun) return;
        $("cam").hidden = false; say(L("Camera ready. Hold the barcode inside the highlighted box."));
        zxReader = new ZXing.BrowserMultiFormatReader();
        starting = false;
        return zxReader.decodeFromConstraints({ video: { facingMode: "environment" } }, video, function (res) {
          if (res && run === scanRun) found(res.getText(), res.getBarcodeFormat());
        });
      });
    }).catch(function (e) {
      if (run !== scanRun) return;
      stop();
      var denied = e && (e.name === "NotAllowedError" || e.name === "SecurityError");
      say(denied ? L("Camera access was blocked. Allow the camera for this site in your browser settings, or use <b>Use a photo</b> instead.")
                 : L("Couldn't start the camera. Use <b>Use a photo</b>, or type the barcode number."));
    });
  }

  function fromPhoto(file) {
    if (!file) return;
    stop();
    if (file.type && file.type.indexOf("image/") !== 0) { say(L("Choose an image file to scan.")); return; }
    if (file.size > 12 * 1024 * 1024) { say(L("Choose a photo smaller than 12 MB, or type the barcode number.")); return; }
    say(L("Reading the photo…"));
    var url = URL.createObjectURL(file);
    var img = new Image();
    img.onload = function () {
      nativeDetector().then(function (det) {
        if (det) return det.detect(img).then(function (c) { return c.length ? { value: c[0].rawValue, format: c[0].format } : null; });
        return loadZxing().then(function () {
          return new ZXing.BrowserMultiFormatReader().decodeFromImageElement(img).then(
            function (r) { return { value: r.getText(), format: r.getBarcodeFormat() }; },
            function () { return null; }
          );
        });
      }).then(function (result) {
        URL.revokeObjectURL(url);
        if (result) handle(result.value, result.format);
        else say(L("No barcode found in that photo. Take it closer, straight on and in good light, or type the numbers under the barcode."));
      }).catch(function () { URL.revokeObjectURL(url); say(L("Couldn't read that photo. Try another one, or type the barcode number.")); });
    };
    img.onerror = function () { URL.revokeObjectURL(url); say(L("That file isn't a photo this browser can open.")); };
    img.src = url;
  }

  $("scanBtn").addEventListener("click", start);
  $("camStop").addEventListener("click", function () { stop(); say(""); });
  $("photoBtn").addEventListener("click", function () { stop(); $("photo").click(); });
  $("photo").addEventListener("change", function () { fromPhoto(this.files[0]); this.value = ""; });
  $("codeForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var v = $("code").value.trim();
    if (/^[\d\s-]+$/.test(v)) v = v.replace(/[\s-]/g, "");  // "3 017620 422003" -> digits only; links keep their dashes
    if (!v) { say(L("Type the numbers printed under the barcode.")); return; }
    handle(v);
  });
  $("clear").addEventListener("click", function () { stop(); $("prod").hidden = true; say(""); $("code").value = ""; });
  window.addEventListener("pagehide", stop);
  // shareable scan link: decoder/#code=3017620422003
  var m = location.hash.match(/^#code=(\d{8,14})$/);
  if (m) lookup(tidy(m[1]));
})();
