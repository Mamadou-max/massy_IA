const ctx = document.getElementById('kpi-chart').getContext('2d');
const kpiChart = new Chart(ctx,{
  type:'line',
  data:{ labels:[], datasets:[{label:'Opportunités',data:[],borderColor:'#3B82F6',backgroundColor:'rgba(59,130,246,0.2)'}] },
  options:{ responsive:true, plugins:{legend:{display:true}} }
});

async function fetchKPIs(){
  const res = await fetch('/api/dashboard/kpis');
  const data = await res.json();
  document.getElementById('kpi-opportunities').textContent = data.opportunities;
  document.getElementById('kpi-risk').textContent = data.risk;
  document.getElementById('kpi-cache').textContent = data.cache;
  kpiChart.data.labels = data.chart.labels;
  kpiChart.data.datasets[0].data = data.chart.data;
  kpiChart.update();
}
fetchKPIs();
