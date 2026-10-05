/* EduTrack VIT — script.js */

// ── Dashboard Charts ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  const CHART_DEFAULTS = {
    color: '#94a3b8',
    font: { family: 'Inter', size: 12 },
  };

  // Doughnut — Enrollment by Course
  const doughnutEl = document.getElementById('chart-enrollment');
  if (doughnutEl) {
    fetch('/api/enrollments-by-course')
      .then(r => r.json())
      .then(({ labels, data }) => {
        new Chart(doughnutEl, {
          type: 'doughnut',
          data: {
            labels,
            datasets: [{
              data,
              backgroundColor: [
                'rgba(99,102,241,0.85)',
                'rgba(139,92,246,0.85)',
                'rgba(6,182,212,0.85)',
                'rgba(16,185,129,0.85)',
                'rgba(245,158,11,0.85)',
                'rgba(244,63,94,0.85)',
              ],
              borderColor: '#161d2f',
              borderWidth: 3,
              hoverOffset: 8,
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '72%',
            plugins: {
              legend: {
                position: 'bottom',
                labels: { color: '#94a3b8', padding: 14, font: { size: 11 }, boxWidth: 12, borderRadius: 4 },
              },
              tooltip: {
                callbacks: {
                  label: ctx => ` ${ctx.label}: ${ctx.parsed} students`,
                },
              },
            },
          },
        });
      });
  }

  // Bar — Monthly Fee Trend
  const barEl = document.getElementById('chart-fees');
  if (barEl) {
    fetch('/api/fee-trend')
      .then(r => r.json())
      .then(({ labels, data }) => {
        new Chart(barEl, {
          type: 'bar',
          data: {
            labels,
            datasets: [{
              label: 'Fee Collected (Rs.)',
              data,
              backgroundColor: 'rgba(99,102,241,0.5)',
              borderColor:     'rgba(99,102,241,0.9)',
              borderWidth: 2,
              borderRadius: 7,
              hoverBackgroundColor: 'rgba(129,140,248,0.7)',
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: ctx => ` Rs. ${ctx.parsed.y.toLocaleString()}`,
                },
              },
            },
            scales: {
              x: {
                grid: { color: 'rgba(37,45,66,0.8)' },
                ticks: { color: '#64748b', font: { size: 11 } },
              },
              y: {
                grid: { color: 'rgba(37,45,66,0.8)' },
                ticks: {
                  color: '#64748b',
                  font: { size: 11 },
                  callback: v => 'Rs. ' + v.toLocaleString(),
                },
                beginAtZero: true,
              },
            },
          },
        });
      });
  }

  // ── Auto-dismiss flash messages after 4 s ───────────────────────────
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // ── Attendance: batch filter triggers reload ─────────────────────────
  const batchSel = document.getElementById('att-batch');
  const dateSel  = document.getElementById('att-date');
  function reloadAttendance() {
    const bid = batchSel ? batchSel.value : '';
    const d   = dateSel  ? dateSel.value  : '';
    if (bid) {
      const url = new URL(window.location.href);
      url.searchParams.set('batch_id', bid);
      url.searchParams.set('date', d);
      window.location.href = url.toString();
    }
  }
  if (batchSel) batchSel.addEventListener('change', reloadAttendance);
  if (dateSel)  dateSel.addEventListener('change', reloadAttendance);

  // ── Student form: filter batches by course ──────────────────────────
  const courseSelect = document.getElementById('course_id');
  const batchSelect  = document.getElementById('batch_id');
  if (courseSelect && batchSelect) {
    const allOptions = Array.from(batchSelect.options);
    courseSelect.addEventListener('change', () => {
      const cid = courseSelect.value;
      batchSelect.innerHTML = '<option value="">— Select batch —</option>';
      allOptions
        .filter(o => o.dataset.course === cid || o.value === '')
        .forEach(o => batchSelect.appendChild(o.cloneNode(true)));
    });
  }
});
