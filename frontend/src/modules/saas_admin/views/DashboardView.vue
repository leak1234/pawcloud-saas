<template>
  <div class="vista">
    <h1 style="margin-bottom: 20px; color: #1e293b;">Resumen del Sistema</h1>
    <div class="kpi-grid">
      <div class="tarjeta-kpi">
        <h3>Total Clínicas</h3>
        <p class="numero">1</p>
      </div>
      <div class="tarjeta-kpi">
        <h3>Clínicas Activas</h3>
        <p class="numero verde">1</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
.tarjeta-kpi { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid #3b82f6; }
.numero { font-size: 32px; font-weight: bold; margin-top: 10px; color: #1e293b; }
.verde { color: #10b981; }
</style>