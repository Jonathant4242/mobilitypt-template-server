// app.js
// DOM wiring only. Uses window.TemplateUX (from ux-lib.js).

(function () {
  "use strict";

  const dateInput = document.getElementById("date");
  const dayInput = document.getElementById("day");
  const timeInput = document.getElementById("time");

  const dateList = document.getElementById("dateOptions");
  const timeList = document.getElementById("timeOptions");

  if (!dateInput || !dayInput || !timeInput) return;
  if (!window.TemplateUX) return;

  function maybeFillDay() {
    const wd = window.TemplateUX.weekdayFromDate(dateInput.value);
    if (!wd) return;

    const current = (dayInput.value || "").trim();

    // Only auto-fill if blank or already matches computed day
    if (!current || current.toLowerCase() === wd.toLowerCase()) {
      dayInput.value = wd;
    }
  }

  // Init
  window.TemplateUX.buildDateOptions(dateList, 14);
  window.TemplateUX.buildTimeOptions(timeList);
  maybeFillDay();

  // Events
  dateInput.addEventListener("input", maybeFillDay);
  dateInput.addEventListener("change", maybeFillDay);
})();