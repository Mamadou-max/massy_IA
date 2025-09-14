const map = L.map('map-container').setView([48.735,2.445],14);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
L.marker([48.735,2.445]).addTo(map).bindPopup("<b>Massy</b><br>Centre-ville");
L.circle([48.735,2.445],{color:'#3B82F6',fillColor:'#3B82F6',fillOpacity:0.2,radius:500}).addTo(map);
