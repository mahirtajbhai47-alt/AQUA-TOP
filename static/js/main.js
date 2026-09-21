/* AquaCare front-end interactions: scroll reveal, counters, navbar, gallery. */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    // --- Navbar shadow on scroll -------------------------------------
    var navbar = document.querySelector(".navbar-aqua");
    if (navbar) {
      var onScroll = function () {
        navbar.classList.toggle("scrolled", window.scrollY > 20);
      };
      onScroll();
      window.addEventListener("scroll", onScroll, { passive: true });
    }

    // --- Reveal on scroll --------------------------------------------
    var revealEls = document.querySelectorAll(".reveal, .reveal-left");
    if ("IntersectionObserver" in window && revealEls.length) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12 });
      revealEls.forEach(function (el) { observer.observe(el); });
    } else {
      revealEls.forEach(function (el) { el.classList.add("visible"); });
    }

    // --- Animated counters -------------------------------------------
    var counters = document.querySelectorAll("[data-counter]");
    var runCounter = function (el) {
      var target = parseInt(el.getAttribute("data-counter"), 10) || 0;
      var duration = 1600;
      var start = null;
      var step = function (ts) {
        if (!start) start = ts;
        var progress = Math.min((ts - start) / duration, 1);
        // easeOutCubic for a smooth finish
        var eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(eased * target).toLocaleString();
        if (progress < 1) requestAnimationFrame(step);
        else el.textContent = target.toLocaleString();
      };
      requestAnimationFrame(step);
    };
    if ("IntersectionObserver" in window && counters.length) {
      var counterObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            runCounter(entry.target);
            counterObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.4 });
      counters.forEach(function (el) { counterObserver.observe(el); });
    } else {
      counters.forEach(runCounter);
    }

    // --- Hero bubbles -------------------------------------------------
    var bubbleWrap = document.querySelector(".hero-bubbles");
    if (bubbleWrap) {
      for (var i = 0; i < 14; i++) {
        var b = document.createElement("span");
        var size = 12 + Math.random() * 54;
        b.className = "bubble";
        b.style.width = size + "px";
        b.style.height = size + "px";
        b.style.left = Math.random() * 100 + "%";
        b.style.animationDuration = 11 + Math.random() * 14 + "s";
        b.style.animationDelay = Math.random() * 10 + "s";
        bubbleWrap.appendChild(b);
      }
    }

    // --- Product image gallery ---------------------------------------
    var mainImage = document.getElementById("productMainImage");
    document.querySelectorAll(".thumb-strip img").forEach(function (thumb) {
      thumb.addEventListener("click", function () {
        if (!mainImage) return;
        mainImage.src = thumb.getAttribute("data-full") || thumb.src;
        document.querySelectorAll(".thumb-strip img").forEach(function (t) {
          t.classList.remove("active");
        });
        thumb.classList.add("active");
      });
    });

    // --- Quantity steppers -------------------------------------------
    document.querySelectorAll("[data-qty-action]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var input = btn.parentElement.querySelector("input[name='quantity']");
        if (!input) return;
        var value = parseInt(input.value, 10) || 1;
        value += btn.getAttribute("data-qty-action") === "plus" ? 1 : -1;
        input.value = Math.max(1, value);
      });
    });

    // --- Auto-dismiss flash messages ---------------------------------
    setTimeout(function () {
      document.querySelectorAll(".alert-dismissible[data-auto-dismiss]").forEach(function (el) {
        if (window.bootstrap && bootstrap.Alert) {
          bootstrap.Alert.getOrCreateInstance(el).close();
        }
      });
    }, 6000);

    // --- Fallback for broken/missing images --------------------------
    document.querySelectorAll("img[data-fallback]").forEach(function (img) {
      img.addEventListener("error", function () {
        if (img.src !== img.getAttribute("data-fallback")) {
          img.src = img.getAttribute("data-fallback");
        }
      });
    });
  });
})();
