/* Lucky Domains interactions */
(function () {
  "use strict";

  // Sticky header shadow
  var header = document.getElementById("site-header");
  function onScroll() {
    if (!header) return;
    header.classList.toggle("scrolled", window.scrollY > 8);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Mobile nav toggle
  var toggle = document.getElementById("nav-toggle");
  if (toggle && header) {
    toggle.addEventListener("click", function () {
      var open = header.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    // Close menu when a link is tapped
    header.querySelectorAll("#nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        header.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
      });
    });
  }

  // FAQ accordion
  document.querySelectorAll(".faq-q").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var expanded = btn.getAttribute("aria-expanded") === "true";
      var panel = btn.nextElementSibling;
      btn.setAttribute("aria-expanded", expanded ? "false" : "true");
      if (panel) panel.style.maxHeight = expanded ? null : panel.scrollHeight + "px";
    });
  });

  // Reveal on scroll
  var reveal = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && reveal.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    reveal.forEach(function (el) { io.observe(el); });
  } else {
    reveal.forEach(function (el) { el.classList.add("in"); });
  }

  // Footer year
  var yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();

  // Contact form (Web3Forms). Replace WEB3FORMS_ACCESS_KEY with your real key.
  var form = document.getElementById("contact-form");
  if (form) {
    var status = document.getElementById("form-status");
    var ACCESS_KEY = form.getAttribute("data-access-key") || "";
    function setStatus(msg, kind) {
      if (!status) return;
      status.textContent = msg;
      status.className = "form-status show " + kind;
    }
    // Prefill the "I need help with" select from ?need=buying|selling|seo (links on Services and the process page).
    var needSel = form.querySelector("#need");
    var needParam = (new URLSearchParams(window.location.search).get("need") || "").toLowerCase();
    if (needSel && needParam) {
      var map = { buying: "Buying a domain", selling: "Selling a domain", seo: "SEO" };
      if (map[needParam]) needSel.value = map[needParam];
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      // Qualifying fields: the form uses novalidate, so check required fields here.
      var missing = [];
      form.querySelectorAll("[required]").forEach(function (el) {
        if (!String(el.value || "").trim()) {
          missing.push(el);
        }
      });
      if (missing.length) {
        setStatus("Please fill in the highlighted fields so Ken can prepare for the call.", "err");
        missing[0].focus();
        return;
      }
      // If the access key hasn't been configured yet, guide instead of failing silently.
      if (!ACCESS_KEY || ACCESS_KEY.indexOf("YOUR_") === 0) {
        setStatus("Form not yet connected. Add your free Web3Forms access key to enable submissions, or email us directly at info@luckydomains.io.", "err");
        return;
      }
      var btn = form.querySelector("button[type=submit]");
      var original = btn ? btn.textContent : "";
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      var data = new FormData(form);
      data.append("access_key", ACCESS_KEY);
      // Put the need and target in the email subject so inquiries are triaged at a glance.
      var need = data.get("need") || "Inquiry";
      var target = data.get("target") || "";
      data.set("subject", "luckydomains.io: " + need + (target ? " / " + target : ""));
      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        body: data,
        headers: { Accept: "application/json" }
      })
        .then(function (r) { return r.json(); })
        .then(function (json) {
          if (json.success) {
            form.reset();
            setStatus("Thanks! Your message is on its way. Ken will reply within one business day.", "ok");
          } else {
            setStatus("Something went wrong. Please email info@luckydomains.io and we'll jump on it.", "err");
          }
        })
        .catch(function () {
          setStatus("Network hiccup. Please email info@luckydomains.io directly.", "err");
        })
        .finally(function () {
          if (btn) { btn.disabled = false; btn.textContent = original; }
        });
    });
  }
})();
