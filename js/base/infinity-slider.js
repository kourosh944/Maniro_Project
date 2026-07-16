/* ==========================================================================
   Maniro — Generic infinite horizontal slider
   Duplicates the cards of a track once, then translates the track with
   requestAnimationFrame using a time-based (not frame-based) step, so the
   loop is perfectly seamless and never jumps or stutters:
     - card widths are measured in real pixels (not %), so exactly
       3 / 2 / 1 cards are visible per breakpoint, always in sync with the
       CSS gap defined for that slider.
     - the position wraps with modulo arithmetic against the exact width
       of one full set of cards, so the reset is invisible.
     - elapsed time between frames is capped, so returning to the tab
       after it was backgrounded never causes a visible skip.
     - hover / keyboard focus pauses the motion; prefers-reduced-motion
       disables it entirely and falls back to a static wrapping layout.

   Multiple sliders can exist on the same page; each is initialized
   independently by initSlider() below.
   ========================================================================== */

(function () {
  "use strict";

  function initSlider(config) {
    var slider = document.getElementById(config.sliderId);
    var track = document.getElementById(config.trackId);
    if (!slider || !track) return;

    var prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;

    var originalCards = Array.prototype.slice.call(
      track.querySelectorAll("." + config.cardClass),
    );
    if (!originalCards.length) return;

    if (prefersReducedMotion) {
      track.classList.add("is-static");
      return;
    }

    // Duplicate the set once so the track can loop seamlessly: as soon as
    // the first set has fully scrolled past, the clone is sitting in the
    // exact same spot the original started in.
    var clones = originalCards.map(function (card) {
      var clone = card.cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      clone.querySelectorAll("a").forEach(function (link) {
        link.setAttribute("tabindex", "-1");
      });
      return clone;
    });
    clones.forEach(function (clone) {
      track.appendChild(clone);
    });

    var perViewByWidth = function (width) {
      if (width <= 640) return 1;
      if (width <= 960) return 2;
      return 3;
    };

    var setWidth = 0; // px width of one full set of (original) cards + gaps
    var x = 0; // current translateX, always <= 0
    var isPaused = false;
    var lastTime = null;
    var speed = config.speed || 75;

    function measure() {
      var viewportWidth = slider.clientWidth;
      var gap =
        parseFloat(
          getComputedStyle(slider).getPropertyValue(config.gapVar),
        ) || 24;
      var perView = perViewByWidth(viewportWidth);
      var cardWidth = (viewportWidth - gap * (perView - 1)) / perView;
      track.style.gap = gap + "px";
      originalCards.concat(clones).forEach(function (card) {
        card.style.flex = "0 0 " + cardWidth + "px";
        card.style.width = cardWidth + "px";
      });

      setWidth =
        originalCards.length * cardWidth + (originalCards.length - 1) * gap;

      // Keep the current scroll position consistent with the new
      // measurements so a resize never causes a visual jump.
      if (setWidth > 0) {
        x = x % setWidth;
        if (x > 0) x -= setWidth;
      }
    }

    function step(time) {
      if (lastTime === null) lastTime = time;
      // Cap the delta so a backgrounded tab (or a slow frame) can never
      // produce a large, visible catch-up jump when it resumes.
      var dt = Math.min(time - lastTime, 50);
      lastTime = time;

      if (!isPaused && setWidth > 0) {
        x -= (speed * dt) / 1000;
        while (x <= -setWidth) {
          x += setWidth;
        }
        track.style.transform = "translate3d(" + -x + "px, 0, 0)";
      }

      requestAnimationFrame(step);
    }

    function pause() {
      isPaused = true;
    }

    function resume() {
      isPaused = false;
    }

    slider.addEventListener("mouseenter", pause);
    slider.addEventListener("mouseleave", resume);
    slider.addEventListener("focusin", pause);
    slider.addEventListener("focusout", resume);

    document.addEventListener("visibilitychange", function () {
      // Force a fresh lastTime reference once the tab is visible again,
      // instead of letting one huge dt slip through.
      if (!document.hidden) lastTime = null;
    });

    var resizeTimer = null;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(measure, 120);
    });

    measure();
    requestAnimationFrame(step);
  }

  // Services slider — homepage "خدمات ما" section.
  initSlider({
    sliderId: "servicesSlider",
    trackId: "servicesTrack",
    cardClass: "service-card",
    gapVar: "--services-gap",
    speed: 75,
  });

  // Values slider — about page "ارزش‌های ما" section.
  initSlider({
    sliderId: "valuesSlider",
    trackId: "valuesTrack",
    cardClass: "value-card",
    gapVar: "--values-gap",
    speed: 75,
  });
})();
