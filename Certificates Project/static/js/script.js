function pollJobStatus() {
  const summaryEl = document.getElementById("job-summary");
  const logEl = document.getElementById("job-log");
  if (!summaryEl || !logEl) return;

  async function tick() {
    try {
      const res = await fetch("/job-status");
      const data = await res.json();

      let summaryText = "";
      if (data.scheduled_for && !data.running && !data.finished) {
        summaryText = `Scheduled for ${data.scheduled_for} — waiting...`;
      } else if (data.running) {
        summaryText = `Sending in progress — Sent: ${data.sent} | Skipped: ${data.skipped} | Total: ${data.total}`;
      } else if (data.finished) {
        summaryText = `Finished — Sent: ${data.sent} | Skipped: ${data.skipped} | Total: ${data.total}`;
      } else {
        summaryText = "No active job.";
      }
      summaryEl.textContent = summaryText;

      logEl.innerHTML = data.log.map(line => `<div>${line}</div>`).join("");
      logEl.scrollTop = logEl.scrollHeight;
    } catch (e) {
      summaryEl.textContent = "Could not fetch job status.";
    }
  }

  tick();
  setInterval(tick, 3000);
}
