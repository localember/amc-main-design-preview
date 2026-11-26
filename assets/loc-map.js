/* Map mockup for the homepage location band. Cards stay on the page for comparison. */
(function () {
  var el = document.getElementById("loc-map");
  var dataEl = document.getElementById("loc-map-data");
  if (!el || !dataEl || !window.L) return;
  var pins;
  try { pins = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var map = L.map(el, { scrollWheelZoom: false, attributionControl: true });
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap"
  }).addTo(map);
  var bounds = [];
  pins.forEach(function (p) {
    var icon = L.divIcon({
      className: "loc-pin",
      html: "<span><b>" + p.short + "</b></span>",
      iconSize: [34, 34],
      iconAnchor: [17, 32],
      popupAnchor: [0, -28]
    });
    var popup = "<strong>" + p.name + "</strong><br>" + p.line1 + "<br>" + p.city +
      "<br><a href=\"tel:" + p.phone + "\">" + p.display + "</a>" +
      "<br><a href=\"" + p.preview + "\" target=\"_blank\" rel=\"noopener\">Location preview</a>";
    L.marker([p.lat, p.lng], { icon: icon, title: p.name, alt: p.name }).addTo(map).bindPopup(popup);
    bounds.push([p.lat, p.lng]);
  });
  if (bounds.length) map.fitBounds(bounds, { padding: [36, 36] });
})();
