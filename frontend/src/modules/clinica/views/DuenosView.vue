<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold text-dark">Directorio de Clientes</h2>
      <button class="btn btn-primary fw-bold" @click="mostrarModalDueno = true">
        + Nuevo Cliente
      </button>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-body p-0">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th class="ps-4">Nombre Completo</th>
              <th>Teléfono</th>
              <th>Correo</th>
              <th class="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colspan="4" class="text-center py-4 text-muted">No hay clientes registrados aún.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const mostrarModalDueno = ref(false);
</script>