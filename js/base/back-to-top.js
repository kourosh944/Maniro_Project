/* ==========================================================================
   Maniro — Back to top button
   Shows the #backToTop button after ~400px of scroll, hides it near the
   top, and scrolls to the top on click. Self-contained: works whether or
   not js/base/smooth-scroll.js is active (reduced motion / touch devices
   skip that engine entirely), by falling back to the browser's native
   smooth scroll, or an instant jump if the user prefers reduced motion.
   ========================================================================== */

(function () {
  "use strict";

  var SHOW_AFTER = 400; // px

  var btn = document.getElementById("backToTop");
  if (!btn) return;

  var prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  var ticking = false;

  function updateVisibility() {
    var y = window.scrollY || window.pageYOffset;
    btn.classList.toggle("is-visible", y > SHOW_AFTER);
    ticking = false;
  }

  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(updateVisibility);
  }

  function scrollToTop() {
    // Prefer the site's custom-eased engine when it's running, so the
    // motion feels identical to wheel scrolling elsewhere on the page.
    if (typeof window.maniroScrollTo === "function") {
      window.maniroScrollTo(0);
      return;
    }

    if (prefersReducedMotion || !("scrollTo" in window)) {
      window.scrollTo(0, 0);
      return;
    }

    window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
  }

  btn.addEventListener("click", scrollToTop);
  window.addEventListener("resize", updateVisibility, { passive: true });
  window.addEventListener("scroll", onScroll, { passive: true });

  updateVisibility(); // Correct initial state on reload with scroll restored.
})();
