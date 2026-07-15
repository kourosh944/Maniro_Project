/* ==========================================================================
   Maniro — Catalog page interactions
   Client-side search / category filter / sort over the demo cards rendered
   in pages/catalog.html.

   IMPORTANT (Django hand-off):
   This script filters DOM nodes that already exist on the page — it does
   not fetch data. Once the grid in pages/catalog.html is replaced by a
   Django `{% for item in items %}` loop, you have two options:
     1) Keep this script as a "instant filter" layer on top of the current
        page of results (no server round-trip while typing).
     2) Replace it with real navigation: submit the search/filter/sort
        controls as a GET form so Django's view can filter/paginate the
        queryset server-side (recommended once the catalog is large).
   Either way, the markup/data attributes below (data-name, data-category)
   are only used by this optional script and are safe to remove if you
   choose option 2.
   ========================================================================== */

(function () {
  "use strict";

  var grid = document.getElementById("catalog-grid");
  if (!grid) return;

  var searchInput = document.getElementById("catalog-search-input");
  var sortSelect = document.getElementById("catalog-sort-select");
  var filterChips = document.querySelectorAll(".catalog-filter-chip");
  var resultsCount = document.getElementById("catalog-results-count");
  var emptyState = document.getElementById("catalog-empty");
  var cards = Array.prototype.slice.call(
    grid.querySelectorAll(".catalog-card")
  );

  var activeCategory = "all";

  function normalize(str) {
    return (str || "").toString().trim().toLowerCase();
  }

  function applyFilters() {
    var query = normalize(searchInput ? searchInput.value : "");
    var visibleCount = 0;

    cards.forEach(function (card) {
      var name = normalize(card.getAttribute("data-name"));
      var category = card.getAttribute("data-category");
      var matchesQuery = !query || name.indexOf(query) !== -1;
      var matchesCategory =
        activeCategory === "all" || category === activeCategory;
      var isVisible = matchesQuery && matchesCategory;

      card.hidden = !isVisible;
      if (isVisible) visibleCount += 1;
    });

    if (resultsCount) {
      resultsCount.textContent =
        visibleCount + " مورد از " + cards.length + " مورد نمایش داده می‌شود";
    }

    if (emptyState) {
      emptyState.classList.toggle("is-visible", visibleCount === 0);
    }
  }

  function applySort() {
    if (!sortSelect) return;
    var value = sortSelect.value;

    var sorted = cards.slice().sort(function (a, b) {
      if (value === "name-asc") {
        return normalize(a.getAttribute("data-name")).localeCompare(
          normalize(b.getAttribute("data-name")),
          "fa"
        );
      }
      if (value === "name-desc") {
        return normalize(b.getAttribute("data-name")).localeCompare(
          normalize(a.getAttribute("data-name")),
          "fa"
        );
      }
      // "newest" (default): preserve original document order
      return cards.indexOf(a) - cards.indexOf(b);
    });

    sorted.forEach(function (card) {
      grid.appendChild(card);
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }

  if (sortSelect) {
    sortSelect.addEventListener("change", applySort);
  }

  filterChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      filterChips.forEach(function (c) {
        c.classList.remove("is-active");
        c.setAttribute("aria-pressed", "false");
      });
      chip.classList.add("is-active");
      chip.setAttribute("aria-pressed", "true");
      activeCategory = chip.getAttribute("data-category-filter") || "all";
      applyFilters();
    });
  });

  // Initial state
  applyFilters();
})();
