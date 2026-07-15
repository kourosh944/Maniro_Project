/* ==========================================================================
   Maniro — Header interactions
   Theme toggle (persisted in localStorage) + mobile nav toggle.
   ========================================================================== */

(function () {
  "use strict";

  var STORAGE_KEY = "maniro-theme";
  var root = document.documentElement;
  var themeToggle = document.getElementById("theme-toggle");
  var menuToggle = document.getElementById("menu-toggle");
  var navLinks = document.getElementById("nav-links");

  function getTheme() {
    return root.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem(STORAGE_KEY, theme);
    if (themeToggle) {
      themeToggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    }
  }

  if (themeToggle) {
    themeToggle.setAttribute("aria-pressed", getTheme() === "dark" ? "true" : "false");
    themeToggle.addEventListener("click", function () {
      setTheme(getTheme() === "dark" ? "light" : "dark");
    });
  }

  // Mobile nav toggle
  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", function () {
      var isOpen = navLinks.classList.toggle("is-open");
      menuToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      menuToggle.setAttribute("aria-label", isOpen ? "بستن منو" : "باز کردن منو");
    });

    // Close mobile nav after choosing a link
    navLinks.querySelectorAll(".nav-link").forEach(function (link) {
      link.addEventListener("click", function () {
        navLinks.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "باز کردن منو");
      });
    });

    // Close on outside click
    document.addEventListener("click", function (event) {
      var isClickInside =
        navLinks.contains(event.target) || menuToggle.contains(event.target);
      if (!isClickInside) {
        navLinks.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "باز کردن منو");
      }
    });

    // Close on Escape and return focus to the toggle button
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && navLinks.classList.contains("is-open")) {
        navLinks.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "باز کردن منو");
        menuToggle.focus();
      }
    });
  }
})();
