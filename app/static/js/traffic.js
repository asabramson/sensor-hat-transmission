async function fetchTrafficLive() {
  try {
    const res = await fetch('/api/traffic/live');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const tbody = document.querySelector('#traffic-table tbody');
    tbody.innerHTML = '';

    data.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.location_id}</td>
        <td>${item.in_count}</td>
        <td>${item.out_count}</td>
        <td>${item.total_in}</td>
        <td>${item.total_out}</td>
        <td>${item.count}</td>
        <td>${item.congestion}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Error loading traffic data:', err);
  }
}

// initial load + repeat every 30 s
fetchTrafficLive();
setInterval(fetchTrafficLive, 30_000);
