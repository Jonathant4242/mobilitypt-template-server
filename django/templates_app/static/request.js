// request.js
// I use this file to handle the scheduling dropdowns on the request page.
// The workflow is simple: the user must pick a day first. Once a day is
// selected, the Date dropdown becomes active and shows the next 12 dates
// for that weekday only. Time dropdowns are still populated on page load.

(function () {
  "use strict";

  const daySelect = document.getElementById("preferred_day");
  const dateSelect = document.getElementById("preferred_date");
  const earliestTimeSelect = document.getElementById("earliest_time");
  const latestTimeSelect = document.getElementById("latest_time");

  if (!daySelect || !dateSelect || !earliestTimeSelect || !latestTimeSelect) return;
  if (!window.TemplateUX) return;

  const WEEKDAYS = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];

  function normalizeWeekday(value) {
    const raw = (value || "").trim().toLowerCase();
    if (!raw) return "";
    return WEEKDAYS.find((day) => day.toLowerCase() === raw) || "";
  }

  function clearAndAddDefault(selectEl, label) {
    selectEl.innerHTML = "";
    const option = document.createElement("option");
    option.value = "";
    option.textContent = label;
    selectEl.appendChild(option);
  }

  function setDateDisabledState(isDisabled) {
    dateSelect.disabled = isDisabled;
  }

  function fillDateOptions(values) {
    clearAndAddDefault(dateSelect, "-- Select Date --");

    values.forEach(function (value) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      dateSelect.appendChild(option);
    });
  }

  function resetDateOptions() {
    clearAndAddDefault(dateSelect, "-- Select Date --");
    setDateDisabledState(true);
  }

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
        results.push(window.TemplateUX.formatDateValue(cursor));
      }
      cursor.setDate(cursor.getDate() + 1);
    }

    return results;
  }

  function fillTimeSelect(selectEl, label) {
    clearAndAddDefault(selectEl, label);

    for (let mins = 8 * 60; mins <= 18 * 60; mins += 30) {
      const option = document.createElement("option");
      option.value = window.TemplateUX.minutesToTimeLabel
        ? window.TemplateUX.minutesToTimeLabel(mins)
        : buildTimeLabelFallback(mins);
      option.textContent = option.value;
      selectEl.appendChild(option);
    }
  }

  function buildTimeLabelFallback(totalMinutes) {
    const h24 = Math.floor(totalMinutes / 60);
    const m = totalMinutes % 60;
    const isPM = h24 >= 12;
    const h12raw = h24 % 12;
    const h12 = h12raw === 0 ? 12 : h12raw;
    return `${h12}:${String(m).padStart(2, "0")} ${isPM ? "PM" : "AM"}`;
  }

  function syncDatesFromDay() {
    const selectedDay = normalizeWeekday(daySelect.value);

    if (!selectedDay) {
      resetDateOptions();
      return;
    }

    fillDateOptions(getNextDatesForWeekday(selectedDay, 12));
    setDateDisabledState(false);
  }

  resetDateOptions();
  fillTimeSelect(earliestTimeSelect, "-- Select Earliest Time --");
  fillTimeSelect(latestTimeSelect, "-- Select Latest Time --");

  daySelect.addEventListener("change", syncDatesFromDay);
})();