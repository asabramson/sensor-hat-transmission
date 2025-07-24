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

const LOCATIONS = [1,2,3,4,5,6];
const TRAFFIC_DAY = 26; // date of presentation session

async function loadTrafficDay(loc, day) {
  const res = await fetch(`/api/traffic/day_series?loc=${loc}&day=${day}`);
  const js  = await res.json();
  const ctx = document.getElementById(`traffic-day-${loc}`).getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: js.hours.map(h => h.toString()),
      datasets: [
        { label: 'Inbound',  data: js.inbound,  fill: false, tension: 0.2, pointRadius: 0 },
        { label: 'Outbound', data: js.outbound, fill: false, tension: 0.2, pointRadius: 0 }
      ]
    },
    options: {
      plugins: {
        decimation: { enabled: true, algorithm: 'lttb', samples: 200 }
      },
      scales: {
        x: { title: { display: true, text: 'Hour' } },
        y: { title: { display: true, text: 'Cars' } }
      }
    }
  });
}

async function loadTrafficMonth(loc) {
  const res = await fetch(`/api/traffic/month_series?loc=${loc}`);
  const js  = await res.json();
  const ctx = document.getElementById(`traffic-month-${loc}`).getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: js.days.map(d => d.toString()),
      datasets: [
        { label: 'Inbound',  data: js.inbound,  fill: false, tension: 0.2, pointRadius: 0 },
        { label: 'Outbound', data: js.outbound, fill: false, tension: 0.2, pointRadius: 0 }
      ]
    },
    options: {
      plugins: {
        decimation: { enabled: true, algorithm: 'lttb', samples: 200 }
      },
      scales: {
        x: { title: { display: true, text: 'Day of Month' } },
        y: { title: { display: true, text: 'Cars' } }
      }
    }
  });
}

// initial load
LOCATIONS.forEach(loc => {
  loadTrafficDay(loc, TRAFFIC_DAY);
  loadTrafficMonth(loc);
});

// initial load + repeat every 30s
fetchTrafficLive();
setInterval(fetchTrafficLive, 30_000);
