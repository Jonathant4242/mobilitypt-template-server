// ux-lib.js
// Helper functions for the Home form (date/time datalists + weekday lookup).
// Kept separate so app.js stays as "DOM wiring only" (no build step needed).
// No event listeners here.

(function () {
  "use strict";

  const HAS_DAYJS = typeof window.dayjs === "function";

  // Enable customParseFormat if the plugin is loaded (optional).
  if (HAS_DAYJS && window.dayjs_plugin_customParseFormat) {
    window.dayjs.extend(window.dayjs_plugin_customParseFormat);
  }

  function pad2(n) {
    return String(n).padStart(2, "0");
  }

  function minutesToTimeLabel(totalMinutes) {
    const h24 = Math.floor(totalMinutes / 60);
    const m = totalMinutes % 60;
    const isPM = h24 >= 12;
    const h12raw = h24 % 12;
    const h12 = h12raw === 0 ? 12 : h12raw;
    return `${h12}:${pad2(m)} ${isPM ? "PM" : "AM"}`;
  }

  // -----------------------------
  // Date formatting / parsing
  // -----------------------------

  function formatDateValue(d) {
    // Server-friendly: "Feb 24, 2026"
    if (HAS_DAYJS) return window.dayjs(d).format("MMM D, YYYY");

    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }

  function formatDateLabel(d) {
    // "Tue Feb 24, 2026"
    if (HAS_DAYJS) return window.dayjs(d).format("ddd MMM D, YYYY");

    const weekday = d.toLocaleDateString("en-US", { weekday: "short" });
    return `${weekday} ${formatDateValue(d)}`;
  }

  function parseFlexibleDate(raw) {
    const s = (raw || "").trim();
    if (!s) return null;

    if (HAS_DAYJS) {
      const formats = ["MMM D, YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "MMM D YYYY"];
      const parsed = window.dayjs(s, formats, true);
      return parsed.isValid() ? parsed : null;
    }

    const d = new Date(s);
    return Number.isNaN(d.getTime()) ? null : d;
  }

  function weekdayFromDate(raw) {
    const parsed = parseFlexibleDate(raw);
    if (!parsed) return "";

    if (HAS_DAYJS) return parsed.format("dddd");

    return parsed.toLocaleDateString("en-US", { weekday: "long" });
  }

  // -----------------------------
  // Builders
  // -----------------------------

  function buildDateOptions(dateListEl, days = 14) {
    if (!dateListEl) return;
    dateListEl.innerHTML = "";

    if (HAS_DAYJS) {
      const today = window.dayjs().startOf("day");
      for (let i = 0; i < days; i++) {
        const d = today.add(i, "day");
        const opt = document.createElement("option");
        opt.value = formatDateValue(d);
        opt.label = formatDateLabel(d);
        dateListEl.appendChild(opt);
      }
      return;
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let i = 0; i < days; i++) {
      const d = new Date(today);
      d.setDate(today.getDate() + i);
      const opt = document.createElement("option");
      opt.value = formatDateValue(d);
      opt.label = formatDateLabel(d);
      dateListEl.appendChild(opt);
    }
  }

  function buildTimeOptions(timeListEl) {
    if (!timeListEl) return;
    timeListEl.innerHTML = "";

    for (let mins = 8 * 60; mins <= 18 * 60; mins += 30) {
      const opt = document.createElement("option");
      opt.value = minutesToTimeLabel(mins);
      timeListEl.appendChild(opt);
    }
  }

  // Expose a tiny API (no imports needed)
  window.TemplateUX = {
    buildDateOptions,
    buildTimeOptions,
    weekdayFromDate,
    formatDateValue,
  };
})();