/* ==========================================================================
   Maniro — Projects Page / Project Showcase Modal
   Static, front-end only: reads placeholder data from each card's
   data-attributes and shows it inside a large showcase modal with
   prev/next navigation, a fullscreen image viewer, keyboard support
   (Esc / Arrow Left / Arrow Right) and touch swipe on mobile.
   No backend involved, no external libraries.
   ========================================================================== */

(function () {
  "use strict";

  var modal = document.getElementById("project-modal");
  if (!modal) return;

  var cards = Array.prototype.slice.call(
    document.querySelectorAll(".project-card")
  );
  if (!cards.length) return;

  var dialog = modal.querySelector(".project-modal-dialog");
  var closeBtn = modal.querySelector(".project-modal-close");
  var counterEl = modal.querySelector('[data-field="counter"]');
  var mediaBtn = modal.querySelector('[data-field="media-btn"]');
  var mediaInnerEl = modal.querySelector('[data-field="media-inner"]');
  var bodyEl = modal.querySelector('[data-field="body"]');
  var titleEl = modal.querySelector('[data-field="title"]');
  var textEl = modal.querySelector('[data-field="description"]');
  var locationEl = modal.querySelector('[data-field="location"]');
  var yearEl = modal.querySelector('[data-field="year"]');
  var typeEl = modal.querySelector('[data-field="type"]');
  var prevBtn = modal.querySelector('[data-nav="prev"]');
  var nextBtn = modal.querySelector('[data-nav="next"]');

  var fullscreen = document.getElementById("project-fullscreen");
  var fullscreenMediaEl = fullscreen
    ? fullscreen.querySelector('[data-field="fullscreen-media"]')
    : null;

  var currentIndex = 0;
  var lastTrigger = null;
  var slideTimer = null;

  /* ---------------- Rendering ---------------- */

  // Reads a card's placeholder <svg> markup so the modal / fullscreen show
  // the same illustration as the card that was clicked.
  function getCardImageMarkup(card) {
    var svg = card.querySelector(".project-card-img svg");
    return svg ? svg.outerHTML : "";
  }

  function renderContent(index) {
    var card = cards[index];
    if (!card) return;

    titleEl.textContent = card.getAttribute("data-title") || "";
    textEl.textContent = card.getAttribute("data-description") || "";
    if (locationEl) locationEl.textContent = card.getAttribute("data-location") || "";
    if (yearEl) yearEl.textContent = card.getAttribute("data-year") || "";
    if (typeEl) typeEl.textContent = card.getAttribute("data-type") || "";
    if (counterEl) counterEl.textContent = (index + 1) + " / " + cards.length;

    var markup = getCardImageMarkup(card);
    if (markup && mediaInnerEl) mediaInnerEl.innerHTML = markup;

    modal.setAttribute("aria-labelledby", "project-modal-title");
  }

  // Animates the body/media out, swaps the data, then animates back in.
  // direction: "next" | "prev" | null (null = no slide, used on first open)
  function goTo(index, direction) {
    var total = cards.length;
    var nextIndex = ((index % total) + total) % total;

    if (!direction) {
      currentIndex = nextIndex;
      renderContent(currentIndex);
      return;
    }

    var outClass = direction === "next" ? "is-sliding-out-next" : "is-sliding-out-prev";

    if (slideTimer) {
      clearTimeout(slideTimer);
      bodyEl.classList.remove("is-sliding-out-next", "is-sliding-out-prev");
      mediaInnerEl.classList.remove("is-sliding-out-next", "is-sliding-out-prev");
    }

    bodyEl.classList.add(outClass);
    mediaInnerEl.classList.add(outClass);

    slideTimer = setTimeout(function () {
      currentIndex = nextIndex;
      renderContent(currentIndex);

      // Force reflow so the re-entry transition actually plays.
      void bodyEl.offsetHeight;

      bodyEl.classList.remove("is-sliding-out-next", "is-sliding-out-prev");
      mediaInnerEl.classList.remove("is-sliding-out-next", "is-sliding-out-prev");
    }, 220);
  }

  function goNext() {
    goTo(currentIndex + 1, "next");
  }

  function goPrev() {
    goTo(currentIndex - 1, "prev");
  }

  /* ---------------- Modal open / close ---------------- */

  function openModal(index, trigger) {
    lastTrigger = trigger || null;
    goTo(index, null);

    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("gallery-modal-open");

    window.requestAnimationFrame(function () {
      closeBtn.focus();
    });
  }

  function closeModal() {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("gallery-modal-open");

    if (lastTrigger) {
      lastTrigger.focus();
      lastTrigger = null;
    }
  }

  function isModalOpen() {
    return modal.classList.contains("is-open");
  }

  /* ---------------- Fullscreen image viewer ---------------- */

  function openFullscreen() {
    if (!fullscreen || !fullscreenMediaEl) return;
    fullscreenMediaEl.innerHTML = mediaInnerEl.innerHTML;
    fullscreen.classList.add("is-open");
    fullscreen.setAttribute("aria-hidden", "false");
  }

  function closeFullscreen() {
    if (!fullscreen) return;
    fullscreen.classList.remove("is-open");
    fullscreen.setAttribute("aria-hidden", "true");
  }

  function isFullscreenOpen() {
    return !!fullscreen && fullscreen.classList.contains("is-open");
  }

  if (mediaBtn) {
    mediaBtn.addEventListener("click", openFullscreen);
  }

  if (fullscreen) {
    fullscreen.querySelectorAll("[data-fullscreen-dismiss]").forEach(function (el) {
      el.addEventListener("click", closeFullscreen);
    });
  }

  /* ---------------- Triggers ---------------- */

  document.querySelectorAll(".project-view-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var card = btn.closest(".project-card");
      var index = cards.indexOf(card);
      if (index === -1) index = 0;
      openModal(index, btn);
    });
  });

  if (closeBtn) closeBtn.addEventListener("click", closeModal);

  modal.querySelectorAll("[data-modal-dismiss]").forEach(function (el) {
    el.addEventListener("click", closeModal);
  });

  if (prevBtn) prevBtn.addEventListener("click", goPrev);
  if (nextBtn) nextBtn.addEventListener("click", goNext);

  /* ---------------- Keyboard support ---------------- */
  // Esc closes the fullscreen viewer first (if open), otherwise the modal.
  // Arrow Left = next project, Arrow Right = previous project — matching
  // the natural forward/back reading direction of this RTL layout.
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      if (isFullscreenOpen()) {
        closeFullscreen();
      } else if (isModalOpen()) {
        closeModal();
      }
      return;
    }

    if (!isModalOpen() || isFullscreenOpen()) return;

    if (event.key === "ArrowLeft") {
      event.preventDefault();
      goNext();
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      goPrev();
    }
  });

  // Keep focus inside the dialog while it is open
  modal.addEventListener("keydown", function (event) {
    if (event.key !== "Tab" || !isModalOpen()) return;

    var focusable = dialog.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusable.length) return;

    var first = focusable[0];
    var last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  /* ---------------- Touch swipe (mobile) ---------------- */
  // Swipe left => next project, swipe right => previous project.
  var touchStartX = 0;
  var touchStartY = 0;
  var touchActive = false;
  var SWIPE_THRESHOLD = 45;

  dialog.addEventListener(
    "touchstart",
    function (event) {
      if (!isModalOpen() || isFullscreenOpen()) return;
      var touch = event.touches[0];
      touchStartX = touch.clientX;
      touchStartY = touch.clientY;
      touchActive = true;
    },
    { passive: true }
  );

  dialog.addEventListener(
    "touchend",
    function (event) {
      if (!touchActive) return;
      touchActive = false;

      var touch = event.changedTouches[0];
      var deltaX = touch.clientX - touchStartX;
      var deltaY = touch.clientY - touchStartY;

      // Ignore mostly-vertical swipes (the user is scrolling the dialog).
      if (Math.abs(deltaX) < SWIPE_THRESHOLD || Math.abs(deltaX) < Math.abs(deltaY)) {
        return;
      }

      if (deltaX < 0) {
        goNext();
      } else {
        goPrev();
      }
    },
    { passive: true }
  );

  // Swipe down on the fullscreen viewer closes it; tap anywhere also closes.
  var fsTouchStartY = 0;
  if (fullscreen) {
    fullscreen.addEventListener(
      "touchstart",
      function (event) {
        fsTouchStartY = event.touches[0].clientY;
      },
      { passive: true }
    );
    fullscreen.addEventListener(
      "touchend",
      function (event) {
        var deltaY = event.changedTouches[0].clientY - fsTouchStartY;
        if (deltaY > 60) closeFullscreen();
      },
      { passive: true }
    );
  }
})();
