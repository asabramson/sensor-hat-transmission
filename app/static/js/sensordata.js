async function fetchSensorData() {
  try {
    const res = await fetch('/api/sensordata/stats');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const tbody = document.querySelector('#sensor-table tbody');
    tbody.innerHTML = '';  // clear old rows

    data.forEach(item => {
      const tr = document.createElement('tr');
      // const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      tr.innerHTML = `
        <td>${item.device_id}</td>
        <td>${item.temperature.toFixed(2)}</td>
        <td>${item.humidity.toFixed(2)}</td>
        <td>${item.pressure.toFixed(2)}</td>
        <td>${new Date(item.timestamp).toLocaleString('en-US')}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Error loading sensor data:', err);
  }
}

async function loadSeries(metric, period, canvasId, label) {
  const res = await fetch(`/api/sensordata/graphs?metric=${metric}&period=${period}`);
  const series = await res.json();
  const labels = series.map(pt => new Date(pt.t).toLocaleTimeString());
  const data   = series.map(pt => pt.v);

  // If we want to limit the max number of data points to show up, use this to select 'labels' and 'data'
  // const maxPoints = 20;
  // let sampled = series;
  // if (series.length > maxPoints) {
  //   const step = Math.ceil(series.length / maxPoints);
  //   sampled = series.filter((_, i) => i % step === 0);
  // }

  // const labels = sampled.map(pt => new Date(pt.t).toLocaleTimeString());
  // const data   = sampled.map(pt => pt.v);

  const ctx = document.getElementById(canvasId).getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: `${label} (${period})`,
        data: data,
        fill: false,
        tension: 0.2,
        pointRadius: 2
      }]
    },
    options: {
      scales: {
        x: { display: true, title: { display: true, text: 'Time' } },
        y: { display: true, title: { display: true, text: label } }
      }
    }
  });
}

// Renders graphs on page reloads
['hour','day','month'].forEach(period => {
  loadSeries('temperature', period, `temp-${period}`, 'Temp (°C)');
  loadSeries('humidity',    period, `hum-${period}`,  'Humidity (%)');
  loadSeries('pressure',    period, `pre-${period}`,  'Pressure (hPa)');
});

fetchSensorData(); // initial fetch
setInterval(fetchSensorData, 15_000); // fetch every 15 seconds
