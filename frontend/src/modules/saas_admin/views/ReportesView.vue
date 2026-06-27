<template>
  <div class="container-fluid">
    <h2 class="mb-4 text-dark fw-bold">Centro de Reportes y Auditoría</h2>
    <p class="text-muted mb-4">Genera y previsualiza reportes operativos en formato PDF. Podrás imprimirlos o descargarlos desde el visor.</p>

    <div class="row g-4">
      <div class="col-md-4">
        <div class="card shadow-sm border-0 border-top border-danger border-4 h-100">
          <div class="card-body text-center py-5">
            <div class="mb-3">
              <span class="fs-1">📝</span>
            </div>
            <h5 class="fw-bold text-dark">Historial de Auditoría</h5>
            <p class="text-muted small px-2">Registro completo de creación, suspensión y edición de clínicas por parte de los administradores.</p>
            <button class="btn btn-danger fw-bold shadow-sm w-100 mt-3" @click="abrirPDF('auditoria')">
              👁️ Ver PDF
            </button>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card shadow-sm border-0 border-top border-success border-4 h-100 bg-light opacity-75">
          <div class="card-body text-center py-5">
            <div class="mb-3">
              <span class="fs-1">💰</span>
            </div>
            <h5 class="fw-bold text-dark">Reporte de Facturación</h5>
            <p class="text-muted small px-2">Historial de renovaciones de planes y cálculo de ingresos mensuales (MRR).</p>
            <button class="btn btn-success fw-bold shadow-sm w-100 mt-3" disabled>
              Próximamente
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const abrirPDF = (tipoReporte) => {
  // Construimos la URL hacia nuestro backend en Flask
  const urlReporte = `http://localhost:5000/api/admin/reportes/pdf/${tipoReporte}`;
  
  // Abrimos la URL en una pestaña nueva para visualizar el documento
  window.open(urlReporte, '_blank');
};
</script>