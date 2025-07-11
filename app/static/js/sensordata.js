async function fetchSensorData() {
  try {
    const res = await fetch('/api/sensordata/stats');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const tbody = document.querySelector('#sensor-table tbody');
    tbody.innerHTML = '';  // clear old rows

    data.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.device_id}</td>
        <td>${item.temperature.toFixed(2)}</td>
        <td>${item.humidity.toFixed(2)}</td>
        <td>${item.pressure.toFixed(2)}</td>
        <td>${new Date(item.timestamp).toLocaleString()}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Error loading sensor data:', err);
  }
}

fetchSensorData(); // initial fetch
setInterval(fetchSensorData, 30_000); // fetch every 30 seconds
