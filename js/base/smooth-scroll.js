/* ==========================================================================
   Maniro — Site-wide smooth scroll (no dependencies)

   Two distinct motions live here, on purpose:

   1) Continuous wheel/trackpad scrolling — accumulate wheel delta and lerp
      the real scroll position toward it every frame. This is a physical
      response to ongoing input, not a fixed-length "animation", so it has
      no set duration (exactly like native OS momentum scrolling).

   2) One-shot navigation jumps — in-page anchor links (e.g. "skip to
      content") and the back-to-top button. These use a formal, capped
      ease-out tween: 220–320ms, no overshoot/bounce, so every jump on the
      site reads as a short, deliberate motion rather than a long scroll.
      window.maniroScrollTo() exposes this for other scripts (back-to-top).

   What this intentionally leaves alone (and why):
     - Touch scrolling: mobile/tablet already has fast, native, GPU-backed
       momentum scrolling. Hijacking it with JS only adds main-thread work
       and typically feels *worse*, so touch/coarse-pointer devices are
       left on native scrolling entirely.
     - Keyboard scrolling (arrows / Page Up-Down / Space) and scrollbar
       dragging: both keep working natively; we only listen for scroll to
       stay in sync, never intercept them.
     - prefers-reduced-motion: the whole engine is skipped, so scrolling
       stays the plain, immediate, native behaviour.

   Performance notes:
     - Only one requestAnimationFrame loop is ever active at a time (wheel
       drag OR a jump, never both) and it fully stops the moment motion
       settles — no idle rAF loop, no per-frame layout reads.
     - The wheel/scroll listeners are the only permanent listeners and do
       no layout work themselves (layout is read once, then cached and
       refreshed only on resize/load).
   ========================================================================== */

(function () {
  "use strict";

  var prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  var isCoarsePointer = window.matchMedia("(pointer: coarse)").matches;

  if (
    prefersReducedMotion ||
    isCoarsePointer ||
    !("requestAnimationFrame" in window)
  ) {
    return; // Native scrolling (already smooth/appropriate) stays untouched.
  }

  var EASE = 0.12; // 0–1: how fast wheel-drag position catches up to target.
  var MIN_DELTA = 0.5; // px: below this, snap and stop the wheel rAF loop.

  var JUMP_MIN_DURATION = 220; // ms — short hops (e.g. a nearby anchor).
  var JUMP_MAX_DURATION = 320; // ms — capped so long jumps still feel brisk.

  var current = getScrollY();
  var target = current;
  var maxScroll = 0;

  var wheelRafId = null; // Drives the continuous wheel-drag lerp.
  var jumpRafId = null; // Drives a one-shot navigation tween.
  var jumpFrom = 0;
  var jumpTo = 0;
  var jumpStartTime = null;
  var jumpDuration = 0;

  // Hand full control of scrollTo() to this engine so our own calls never
  // get re-animated by the CSS `scroll-behavior: smooth` on top of our
  // own easing (which would look laggy/double-smoothed).
  var htmlEl = document.documentElement;
  var previousCssScrollBehavior = htmlEl.style.scrollBehavior;
  htmlEl.style.scrollBehavior = "auto";

  function getScrollY() {
    return window.scrollY || window.pageYOffset;
  }

  function clamp(value, min, max) {
    return value < min ? min : value > max ? max : value;
  }

  // Formal, symmetrical deceleration — no overshoot, no bounce.
  // Equivalent feel to the site's --ease token (cubic-bezier(.4,0,.2,1)).
  function easeOutCubic(t) {
    var p = t - 1;
    return p * p * p + 1;
  }

  function recalcMaxScroll() {
    maxScroll = Math.max(htmlEl.scrollHeight - window.innerHeight, 0);
    target = clamp(target, 0, maxScroll);
  }

  function isOptedOut(el) {
    return !!(el && el.closest && el.closest("[data-native-scroll]"));
  }

  function cancelWheelLoop() {
    if (wheelRafId !== null) {
      cancelAnimationFrame(wheelRafId);
      wheelRafId = null;
    }
  }

  function cancelJump() {
    if (jumpRafId !== null) {
      cancelAnimationFrame(jumpRafId);
      jumpRafId = null;
    }
  }

  function requestWheelTick() {
    if (wheelRafId === null) {
      wheelRafId = requestAnimationFrame(updateWheel);
    }
  }

  function updateWheel() {
    current += (target - current) * EASE;

    if (Math.abs(target - current) < MIN_DELTA) {
      current = target;
      window.scrollTo(0, current);
      wheelRafId = null;
      return;
    }

    window.scrollTo(0, current);
    wheelRafId = requestAnimationFrame(updateWheel);
  }

  function onWheel(e) {
    // Let the browser handle: pinch-zoom (ctrl+wheel), anything already
    // handled, and any explicitly opted-out scroll container.
    if (e.ctrlKey || e.defaultPrevented || isOptedOut(e.target)) return;

    var delta = e.deltaY;
    if (e.deltaMode === 1) delta *= 18; // DOM_DELTA_LINE -> px
    else if (e.deltaMode === 2) delta *= window.innerHeight; // DOM_DELTA_PAGE -> px

    if (delta === 0) return; // e.g. pure horizontal wheel gesture

    e.preventDefault();

    // Wheel input always wins: interrupt any in-flight navigation jump
    // and resume continuous scrolling from exactly where things are.
    if (jumpRafId !== null) {
      cancelJump();
      current = target = getScrollY();
    }

    target = clamp(target + delta, 0, maxScroll);
    requestWheelTick();
  }

  function onScroll() {
    if (wheelRafId !== null || jumpRafId !== null) return; // Our own motion.
    // Someone scrolled another way (scrollbar drag, keyboard, browser
    // autoscroll): resync so the next wheel tick continues smoothly from
    // here instead of jumping back to a stale target.
    current = target = getScrollY();
  }

  function updateJump(timestamp) {
    if (jumpStartTime === null) jumpStartTime = timestamp;
    var elapsed = timestamp - jumpStartTime;
    var t = clamp(elapsed / jumpDuration, 0, 1);
    var eased = easeOutCubic(t);
    var y = jumpFrom + (jumpTo - jumpFrom) * eased;

    current = target = y;
    window.scrollTo(0, y);

    if (t < 1) {
      jumpRafId = requestAnimationFrame(updateJump);
    } else {
      jumpRafId = null;
    }
  }

  // Short, deliberate, duration-capped navigation jump — used for in-page
  // anchors and exposed as window.maniroScrollTo() for the back-to-top
  // button. Distinct from the continuous wheel-drag loop above.
  function animateTo(top) {
    cancelWheelLoop();
    cancelJump();

    var from = getScrollY();
    var to = clamp(top, 0, maxScroll);
    var distance = Math.abs(to - from);

    if (distance < 1) {
      window.scrollTo(0, to);
      current = target = to;
      return;
    }

    jumpFrom = from;
    jumpTo = to;
    jumpStartTime = null;
    // Slightly longer for longer jumps, but always within the site's
    // 200–350ms motion spec — never a slow, dragged-out scroll.
    jumpDuration = clamp(
      JUMP_MIN_DURATION + distance * 0.04,
      JUMP_MIN_DURATION,
      JUMP_MAX_DURATION
    );

    jumpRafId = requestAnimationFrame(updateJump);
  }

  function onAnchorClick(e) {
    var link = e.target.closest && e.target.closest('a[href^="#"]');
    if (!link || isOptedOut(link)) return;

    var hash = link.getAttribute("href");
    if (!hash || hash === "#") return;

    var destination;
    try {
      destination = document.getElementById(hash.slice(1));
    } catch (err) {
      return;
    }
    if (!destination) return;

    e.preventDefault();
    recalcMaxScroll();
    var top = destination.getBoundingClientRect().top + window.scrollY;
    animateTo(top);

    if (history.pushState) {
      history.pushState(null, "", hash);
    }
  }

  // Small public hook so other same-site scripts (e.g. the back-to-top
  // button) can trigger the same short, formal jump instead of
  // reimplementing it. No-op / absent when this engine bailed out above
  // (reduced motion, touch, unsupported browser) — callers should treat
  // it as optional and fall back to native scrolling if it's missing.
  window.maniroScrollTo = animateTo;

  recalcMaxScroll();

  window.addEventListener("wheel", onWheel, { passive: false });
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", recalcMaxScroll, { passive: true });
  window.addEventListener("load", recalcMaxScroll, { passive: true });
  document.addEventListener("click", onAnchorClick);

  window.addEventListener("pagehide", function () {
    cancelWheelLoop();
    cancelJump();
    htmlEl.style.scrollBehavior = previousCssScrollBehavior;
  });
})();
