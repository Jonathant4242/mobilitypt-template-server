(function () {
  const modal = document.getElementById('generate-modal');
  const backdrop = document.getElementById('generate-modal-backdrop');
  const closeButton = document.getElementById('close-generate-modal');
  const form = document.getElementById('generate-modal-form');
  const rowIndexInput = document.getElementById('generate_row_index');
  const subtitle = document.getElementById('generate-modal-subtitle');
  const dayInput = document.getElementById('generate_day');
  const dateInput = document.getElementById('generate_date');
  const timeSelect = document.getElementById('generate_time_select');
  const timeCustom = document.getElementById('generate_time_custom');
  const timeHidden = document.getElementById('generate_time');
  const openButtons = document.querySelectorAll('.open-generate-modal');

  if (
    !modal ||
    !backdrop ||
    !closeButton ||
    !form ||
    !rowIndexInput ||
    !subtitle ||
    !dayInput ||
    !dateInput ||
    !timeSelect ||
    !timeCustom ||
    !timeHidden
  ) {
    return;
  }

  const weekdayMap = {
    Monday: 1,
    Tuesday: 2,
    Wednesday: 3,
    Thursday: 4,
    Friday: 5,
  };

  function formatDate(date) {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }

  function nextDatesForWeekday(dayName, count) {
    const target = weekdayMap[dayName];
    if (!target) {
      return [];
    }

    const results = [];
    const current = new Date();
    current.setHours(0, 0, 0, 0);

    const candidate = new Date(current);
    while (candidate.getDay() !== target) {
      candidate.setDate(candidate.getDate() + 1);
    }

    for (let i = 0; i < count; i += 1) {
      results.push(new Date(candidate));
      candidate.setDate(candidate.getDate() + 7);
    }

    return results;
  }

  function populateGenerateDates() {
    const selectedDay = dayInput.value;
    dateInput.innerHTML = '<option value="">-- Select Date --</option>';

    if (!selectedDay) {
      dateInput.disabled = true;
      return;
    }

    const dates = nextDatesForWeekday(selectedDay, 12);
    dates.forEach((date) => {
      const option = document.createElement('option');
      option.value = formatDate(date);
      option.textContent = formatDate(date);
      dateInput.appendChild(option);
    });

    dateInput.disabled = false;
  }

  function syncGenerateTime() {
    const customValue = timeCustom.value.trim();
    if (customValue) {
      timeHidden.value = customValue;
      return;
    }

    if (timeSelect.value && timeSelect.value !== 'Custom') {
      timeHidden.value = timeSelect.value;
      return;
    }

    timeHidden.value = '';
  }

  function resetModalFields() {
    dayInput.value = '';
    dateInput.innerHTML = '<option value="">-- Select Date --</option>';
    dateInput.disabled = true;
    timeSelect.value = '';
    timeCustom.value = '';
    timeHidden.value = '';
  }

  function openModal(rowIndex, patientName) {
    resetModalFields();
    rowIndexInput.value = rowIndex || '';
    subtitle.textContent = patientName
      ? `Waitlist Opening template ready for ${patientName}. Enter the opening details below.`
      : 'Enter the opening details, then generate the message.';
    modal.style.display = 'block';
    backdrop.style.display = 'block';
    dayInput.focus();
  }

  function closeModal() {
    modal.style.display = 'none';
    backdrop.style.display = 'none';
  }

  openButtons.forEach((button) => {
    button.addEventListener('click', function () {
      openModal(button.dataset.rowIndex, button.dataset.patient || '');
    });
  });

  closeButton.addEventListener('click', closeModal);
  backdrop.addEventListener('click', closeModal);
  dayInput.addEventListener('change', populateGenerateDates);
  timeSelect.addEventListener('change', syncGenerateTime);
  timeCustom.addEventListener('input', syncGenerateTime);

  form.addEventListener('submit', function () {
    syncGenerateTime();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && modal.style.display === 'block') {
      closeModal();
    }
  });
})();
