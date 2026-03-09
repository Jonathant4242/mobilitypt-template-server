// app.js
// I use this file to handle the page behavior for the Home form.
// It connects the form inputs to the shared helper logic in ux-lib.js.
// I keep the event listeners here so this file stays focused on DOM wiring.
// ux-lib.js must load first so window.TemplateUX is available.

(function () {
  "use strict";

  // I grab the main form inputs the user works with.
  // These map to the Day, Date, and Time fields on the page.
  const dateInput = document.getElementById("date");
  const dayInput = document.getElementById("day");
  const timeInput = document.getElementById("time");
  const form = document.querySelector("form");
  const templateSelect = document.getElementById("template");
  const quickButtons = document.querySelectorAll(".quick-buttons button");

  // These elements hold the available date and time options.
  // I update them dynamically based on the current form state.
  const timeList = document.getElementById("timeOptions");

  if (!dateInput || !dayInput || !timeInput) return;
  if (!window.TemplateUX) return;

  // -----------------------------
  // Weekday normalization helpers
  // -----------------------------

  // I keep a weekday list here so I can normalize user input
  // and compare weekday values consistently.
  const WEEKDAYS = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];

  // I normalize values such as "fri" or "Friday"
  // into a consistent weekday name the program can use.
  function normalizeWeekday(value) {
    const raw = (value || "").trim().toLowerCase();
    if (!raw) return "";

    return WEEKDAYS.find((day) => day.toLowerCase().startsWith(raw)) || "";
  }

  // I format dates locally as a fallback in case the shared helper
  // is not available in the browser yet.
  function formatDateValueSafe(d) {
    if (window.TemplateUX && typeof window.TemplateUX.formatDateValue === "function") {
      return window.TemplateUX.formatDateValue(d);
    }

    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }

  // -----------------------------
  // Date generation helpers
  // -----------------------------

  // When the user chooses a weekday, I generate the next
  // matching dates starting from today.
  function getNextDatesForWeekday(weekday, count) {
    const canonical = normalizeWeekday(weekday);
    if (!canonical) return [];

    const targetIndex = WEEKDAYS.indexOf(canonical);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const results = [];
    const cursor = new Date(today);

    while (results.length < count) {
      if (cursor.getDay() === targetIndex) {
        results.push(formatDateValueSafe(cursor));
      }
      cursor.setDate(cursor.getDate() + 1);
    }

    return results;
  }

  // -----------------------------
  // Date suggestion list helpers
  // -----------------------------

  // I replace the current date options with a new list.
  // I use this when the user selects a weekday.
  function replaceDateOptions(values) {
    if (!dateInput) return;

    const currentValue = dateInput.value;
    dateInput.innerHTML = "";

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "-- Select Date --";
    dateInput.appendChild(defaultOption);

    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      dateInput.appendChild(option);
    });

    if (values.includes(currentValue)) {
      dateInput.value = currentValue;
    }
  }

  // I restore the default list of upcoming dates if the user
  // clears the weekday input field.
  function restoreDefaultDateOptions() {
    if (!dateInput) return;

    const currentValue = dateInput.value;
    dateInput.innerHTML = "";

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "-- Select Date --";
    dateInput.appendChild(defaultOption);

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const values = [];
    for (let i = 0; i < 14; i++) {
      const d = new Date(today);
      d.setDate(today.getDate() + i);
      values.push(formatDateValueSafe(d));
    }

    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      dateInput.appendChild(option);
    });

    if (values.includes(currentValue)) {
      dateInput.value = currentValue;
    }
  }

  // -----------------------------
  // Day / Date sync logic
  // -----------------------------

  // If the user picks a date, I automatically fill the weekday
  // field so both values stay in sync.
  function maybeFillDay() {
    const wd = window.TemplateUX.weekdayFromDate(dateInput.value);
    if (!wd) return;

    const current = normalizeWeekday(dayInput.value);

    // Only auto-fill if blank or already matches computed day
    if (!current || current.toLowerCase() === wd.toLowerCase()) {
      dayInput.value = wd;
    }
  }

  // When the weekday changes, I update the date suggestions
  // so only matching dates appear in the list.
  function syncFromDay() {
    const canonical = normalizeWeekday(dayInput.value);

    if (!canonical) {
      restoreDefaultDateOptions();
      return;
    }

    dayInput.value = canonical;
    replaceDateOptions(getNextDatesForWeekday(canonical, 12));

    const selectedWeekday = window.TemplateUX.weekdayFromDate(dateInput.value);
    if (dateInput.value && selectedWeekday && selectedWeekday !== canonical) {
      dateInput.value = "";
    }
  }

  // If the date is cleared, I reset the form behavior
  // so the user can choose either a day or a date again.
  function clearDayModeIfDateRemoved() {
    if (dateInput.value) return;

    if (!normalizeWeekday(dayInput.value)) {
      restoreDefaultDateOptions();
    }
  }

  // -----------------------------
  // Initialization
  // -----------------------------

  // I run this setup when the page loads.
  // It builds the date and time suggestions and syncs the fields.
  restoreDefaultDateOptions();
  window.TemplateUX.buildTimeOptions(timeList);
  maybeFillDay();
  syncFromDay();
  clearDayModeIfDateRemoved();

  // -----------------------------
  // Event listeners
  // -----------------------------

  // I keep the event listeners here so the UI stays in sync
  // as the user edits the form.
  dateInput.addEventListener("change", function () {
    maybeFillDay();
    clearDayModeIfDateRemoved();
  });

  dayInput.addEventListener("change", syncFromDay);

  if (form) {
    form.addEventListener("reset", function () {
      setTimeout(function () {
        // Restore the Day field to its default blank option.
        if (dayInput) {
          dayInput.value = "";
        }

        // Remove any hidden quick-message option that may have been added.
        if (templateSelect) {
          Array.from(templateSelect.options).forEach(function (opt) {
            if (opt.hidden) {
              opt.remove();
            }
          });
          templateSelect.value = "";
        }

        // Clear the Time field and rebuild its suggestions.
        if (timeInput) {
          timeInput.value = "";
        }
        window.TemplateUX.buildTimeOptions(timeList);

        // Rebuild the default Date dropdown and clear its selection.
        restoreDefaultDateOptions();
        if (dateInput) {
          dateInput.value = "";
        }
      }, 0);
    });
  }

  // -----------------------------
  // Quick Message Buttons
  // -----------------------------

  // I use these buttons to select a no-field template and
  // submit the form so the preview is generated right away.
  quickButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const templateName = btn.dataset.template;

      if (templateSelect && templateName) {
        let option = Array.from(templateSelect.options).find(function (opt) {
          return opt.value === templateName;
        });

        if (!option) {
          option = document.createElement("option");
          option.value = templateName;
          option.textContent = templateName;
          option.hidden = true;
          templateSelect.appendChild(option);
        }

        templateSelect.value = templateName;
      }

      if (form) {
        form.submit();
      }
    });
  });
})();