/* The whole client-side script for the site. No framework: the state here is
   local and tiny (the chosen theme, a search box, a category filter), so plain
   DOM code is the shortest honest answer.

   Degrades cleanly: with JavaScript off the complete page is still there, all
   themes are still listed, and the default Monkeytype theme applies. */
(function () {
  "use strict";

  var STORE_KEY = "mt_theme";
  var THEME_COUNT = document.querySelectorAll(".theme-item").length;

  var root = document.documentElement;
  var picker = document.getElementById("theme-list");
  var search = document.getElementById("theme-search");
  var kindFilter = document.getElementById("theme-filter");
  var count = document.getElementById("theme-count");
  var emptyNote = document.getElementById("theme-empty");
  var preview = document.getElementById("theme-preview");
  var currentLabel = document.getElementById("theme-current");

  /* ---------------------------------------------------------------- themes */

  function currentTheme() {
    return root.getAttribute("data-theme") || "";
  }

  function applyTheme(name, remember) {
    root.setAttribute("data-theme", name);
    if (preview) preview.setAttribute("data-theme", name);
    if (currentLabel) currentLabel.textContent = name;
    if (remember) {
      try { localStorage.setItem(STORE_KEY, name); } catch (e) { /* private mode */ }
    }
    document.querySelectorAll("[data-theme-name]").forEach(function (el) {
      el.setAttribute("aria-current",
        el.getAttribute("data-theme-name") === name ? "true" : "false");
    });
  }

  function previewTheme(name) {
    if (preview) preview.setAttribute("data-theme", name);
  }

  /* --------------------------------------------------------------- picker */

  function isVisible(row) {
    if (!search || !kindFilter) return true;
    var query = search.value.trim().toLowerCase();
    if (query && row.getAttribute("data-name").indexOf(query) === -1) return false;
    var kind = kindFilter.value;
    if (kind === "all") return true;
    return (row.getAttribute("data-flags") || "").indexOf(kind) !== -1;
  }

  function refreshPicker() {
    if (!picker) return;
    var shown = 0;
    picker.querySelectorAll(".theme-item").forEach(function (row) {
      var keep = isVisible(row);
      row.hidden = !keep;
      if (keep) shown++;
    });
    if (count) count.textContent = shown + " of " + THEME_COUNT + " themes";
    if (emptyNote) emptyNote.hidden = shown !== 0;
  }

  if (picker) {
    picker.addEventListener("click", function (evt) {
      var row = evt.target.closest(".theme-item");
      if (row) applyTheme(row.getAttribute("data-theme-name"), true);
    });
    /* hovering or focusing a row previews it in the pane, without committing */
    picker.addEventListener("mouseover", function (evt) {
      var row = evt.target.closest(".theme-item");
      if (row) previewTheme(row.getAttribute("data-theme-name"));
    });
    picker.addEventListener("focusin", function (evt) {
      var row = evt.target.closest(".theme-item");
      if (row) previewTheme(row.getAttribute("data-theme-name"));
    });
    picker.addEventListener("mouseleave", function () { previewTheme(currentTheme()); });
    picker.addEventListener("focusout", function (evt) {
      if (!picker.contains(evt.relatedTarget)) previewTheme(currentTheme());
    });
  }

  if (search) {
    search.addEventListener("input", refreshPicker);
    search.addEventListener("search", refreshPicker);
  }
  if (kindFilter) kindFilter.addEventListener("change", refreshPicker);

  var random = document.getElementById("theme-random");
  if (random) {
    random.addEventListener("click", function () {
      var rows = Array.prototype.filter.call(
        picker.querySelectorAll(".theme-item"), function (r) { return !r.hidden; }
      );
      if (!rows.length) return;
      var choice = rows[Math.floor(Math.random() * rows.length)];
      applyTheme(choice.getAttribute("data-theme-name"), true);
      choice.scrollIntoView({ block: "nearest" });
    });
  }

  /* ------------------------------------------------------------ shortcuts */

  document.addEventListener("keydown", function (evt) {
    if (evt.key === "Escape" && document.activeElement === search) {
      search.value = "";
      refreshPicker();
      search.blur();
      return;
    }
    if (evt.key !== "/" || evt.metaKey || evt.ctrlKey || evt.altKey) return;
    var tag = (evt.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || tag === "select") return;
    if (!search) return;
    evt.preventDefault();
    search.focus();
    search.select();
  });

  /* the inline <head> script already applied the saved theme before first paint;
     this keeps the labels and the preview pane in step with it */
  applyTheme(currentTheme(), false);
  refreshPicker();
})();
