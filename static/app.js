const API = "";
let map = null;
let markerLayer = null;
let fittedInitialMap = false;

function safe(value) {
  return String(value ?? "—").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
}
function fmtDate(value) {
  if (!value) return "Sin mensajes";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Fecha no válida";
  return date.toLocaleString("es-PE", { dateStyle: "short", timeStyle: "short" });
}
function setConnection(connected, message) {
  document.getElementById("connection-label").textContent = message;
  document.getElementById("connection-dot").classList.toggle("offline", !connected);
}
function statusInfo(device) {
  if (!device.online) return { label: "Sin comunicación", css: "offline", color: "#87928e" };
  if (device.alert_level === "alert") return { label: "Alerta", css: "alert", color: "#c8443d" };
  if (device.alert_level === "prealert") return { label: "Prealerta", css: "prealert", color: "#d59428" };
  return { label: "Normal", css: "normal", color: "#168052" };
}
function initializeMap() {
  const mapElement = document.getElementById("map");
  if (!window.L) {
    mapElement.innerHTML = '<p class="map-fallback">No se pudo cargar Leaflet. El mapa requiere conexión a Internet en esta versión; los demás paneles pueden funcionar.</p>';
    return;
  }
  map = L.map("map").setView([-13.53195, -71.96746], 11);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);
  markerLayer = L.layerGroup().addTo(map);
}
function renderDevices(devices) {
  document.getElementById("node-count").textContent = `${devices.length} nodos`;
  const body = document.getElementById("devices-body");
  body.innerHTML = devices.length ? devices.map(d => {
    const s = statusInfo(d);
    const battery = d.battery_v == null ? "—" : `${Number(d.battery_v).toFixed(2)} V`;
    return `<tr><td><span class="device-name">${safe(d.name)}</span><span class="subline">${safe(d.id)}</span></td><td><span class="state state-${s.css}">${s.label}</span></td><td>${safe(battery)}</td><td>${safe(fmtDate(d.last_seen))}</td></tr>`;
  }).join("") : '<tr><td colspan="4" class="empty">No hay nodos registrados. Ejecuta scripts/seed_demo.py para crear datos ficticios.</td></tr>';

  if (!map || !markerLayer) return;
  markerLayer.clearLayers();
  devices.forEach(d => {
    const s = statusInfo(d);
    const marker = L.circleMarker([d.latitude, d.longitude], {
      radius: 9, color: "#fff", weight: 2, fillColor: s.color, fillOpacity: .95
    }).addTo(markerLayer);
    marker.bindPopup(`<strong>${safe(d.name)}</strong><br>ID: ${safe(d.id)}<br>Estado: ${s.label}<br>Batería: ${d.battery_v == null ? "—" : safe(d.battery_v) + " V"}<br>Ubicación: ${safe(d.location_note)}`);
  });
  if (!fittedInitialMap && devices.length === 1) {
    map.setView([devices[0].latitude, devices[0].longitude], 13);
    fittedInitialMap = true;
  } else if (!fittedInitialMap && devices.length > 1) {
    const bounds = L.latLngBounds(devices.map(d => [d.latitude, d.longitude]));
    map.fitBounds(bounds.pad(.25), { maxZoom: 13 });
    fittedInitialMap = true;
  }
}
function renderAlerts(alerts) {
  const el = document.getElementById("alerts-list");
  if (!alerts.length) {
    el.innerHTML = '<p class="empty">Todavía no hay alertas registradas.</p>';
    return;
  }
  el.innerHTML = alerts.map(a => {
    const isAlert = a.level === "alert";
    const label = isAlert ? "Posible incendio" : "Prealerta ambiental";
    const css = isAlert ? "alert" : "prealert";
    return `<div class="alert-row ${css}"><div class="alert-symbol">${isAlert ? "!" : "△"}</div><div><p class="alert-title">${label} · ${safe(a.node_id)}</p><p class="alert-meta">${safe(a.message)} · ${safe(fmtDate(a.created_at))}${a.acknowledged ? " · Atendida" : ""}</p></div>${a.acknowledged ? "" : `<button class="ack-btn" data-alert-id="${Number(a.id)}">Marcar atendida</button>`}</div>`;
  }).join("");
  el.querySelectorAll("[data-alert-id]").forEach(button => button.addEventListener("click", async () => {
    try {
      const response = await fetch(`${API}/api/alerts/${button.dataset.alertId}/ack`, { method: "POST" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      await refresh();
    } catch (error) {
      setConnection(false, "Error al actualizar alerta");
      console.error(error);
    }
  }));
}
function renderReading(readings) {
  const el = document.getElementById("latest-reading");
  if (!readings.length) {
    el.innerHTML = '<p class="empty">Aún no se han recibido mediciones.</p>';
    return;
  }
  const r = readings[0];
  const metrics = [
    ["Dispositivo", r.node_id],
    ["Temperatura", r.temperature_c == null ? "—" : `${r.temperature_c} °C`],
    ["Humedad", r.humidity_pct == null ? "—" : `${r.humidity_pct} %`],
    ["Lectura de humo (ADC)", r.smoke_raw == null ? "—" : r.smoke_raw],
    ["Batería", r.battery_v == null ? "—" : `${r.battery_v} V`],
    ["Recibido", fmtDate(r.received_at)],
  ];
  el.innerHTML = metrics.map(([label, value]) => `<div class="reading-metric"><span>${safe(label)}</span><strong>${safe(value)}</strong></div>`).join("");
}
async function jsonFetch(path) {
  const response = await fetch(`${API}${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
async function refresh() {
  try {
    const [overview, devices, alerts, readings] = await Promise.all([
      jsonFetch("/api/overview"),
      jsonFetch("/api/devices"),
      jsonFetch("/api/alerts?limit=12"),
      jsonFetch("/api/readings?limit=1")
    ]);
    document.getElementById("total-nodes").textContent = overview.total_nodes;
    document.getElementById("online-nodes").textContent = overview.online_nodes;
    document.getElementById("offline-nodes").textContent = overview.offline_nodes;
    document.getElementById("active-alerts").textContent = overview.unacknowledged_alerts;
    renderDevices(devices);
    renderAlerts(alerts);
    renderReading(readings);
    setConnection(true, "Servidor conectado");
  } catch (error) {
    setConnection(false, "Sin conexión al servidor");
    console.error("No se pudo actualizar ForestGuard:", error);
  }
}

initializeMap();
refresh();
setInterval(refresh, 5000);
