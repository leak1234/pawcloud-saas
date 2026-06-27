<template>
  <div class="card shadow-sm border-0" :class="{'border-primary border-2': avisoEditando}">
    <div class="card-header text-white fw-bold d-flex justify-content-between align-items-center" 
         :class="avisoEditando ? 'bg-primary' : 'bg-dark'">
      <span>{{ avisoEditando ? '✏️ Editando Aviso' : 'Redactar Nuevo Aviso' }}</span>
      <button v-if="avisoEditando" @click="cancelar" class="btn btn-sm btn-light text-primary fw-bold shadow-sm">
        ✕ Cancelar
      </button>
    </div>
    <div class="card-body bg-light">
      <form @submit.prevent="guardar">
        <div class="mb-3">
          <label class="form-label fw-bold text-secondary small">Título del Aviso *</label>
          <input type="text" class="form-control fw-bold" v-model="form.titulo" placeholder="Ej: Mantenimiento Programado" required maxlength="150">
        </div>
        
        <div class="mb-3">
          <label class="form-label fw-bold text-secondary small">Tipo de Mensaje *</label>
          <select class="form-select fw-semibold" v-model="form.tipo" required>
            <option value="info">🔵 Informativo (Actualizaciones, Noticias)</option>
            <option value="warning">🟡 Precaución (Recordatorios, Cambios)</option>
            <option value="danger">🔴 Urgente (Mantenimiento, Caídas)</option>
          </select>
        </div>
        
        <div class="mb-3">
          <label class="form-label fw-bold text-secondary small">Mensaje Detallado *</label>
          <textarea class="form-control" v-model="form.mensaje" rows="5" placeholder="Escribe el contenido del comunicado aquí..." required maxlength="2000"></textarea>
          <div class="text-end text-muted" style="font-size: 0.7rem;">
            {{ form.mensaje.length }} / 2000
          </div>
        </div>
        
        <button type="submit" class="btn w-100 fw-bold shadow-sm" :class="avisoEditando ? 'btn-primary' : 'btn-dark'" :disabled="loading">
          {{ avisoEditando ? '💾 Guardar Cambios' : '✈️ Publicar a todas las Clínicas' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import Swal from 'sweetalert2';

const props = defineProps({
  avisoEditando: Object // Si es null, estamos creando. Si tiene datos, estamos editando.
});

const emit = defineEmits(['actualizar-lista', 'cancelar-edicion']);

const loading = ref(false);
const form = ref({ titulo: '', tipo: 'info', mensaje: '' });

// Escuchar cambios en las props para llenar el formulario si el Padre pide editar
watch(() => props.avisoEditando, (nuevoAviso) => {
  if (nuevoAviso) {
    form.value = { ...nuevoAviso };
  } else {
    form.value = { titulo: '', tipo: 'info', mensaje: '' };
  }
});

const cancelar = () => {
  form.value = { titulo: '', tipo: 'info', mensaje: '' };
  emit('cancelar-edicion');
};

const guardar = async () => {
  loading.value = true;
  const modoEdicion = !!props.avisoEditando;
  const url = modoEdicion 
    ? `http://localhost:5000/api/admin/avisos/${props.avisoEditando.id}` 
    : 'http://localhost:5000/api/admin/avisos';
  const metodo = modoEdicion ? 'PUT' : 'POST';

  try {
    const respuesta = await fetch(url, {
      method: metodo,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    });
    
    if (respuesta.ok) {
      Swal.fire({
        toast: true, position: 'top-end', icon: 'success',
        title: modoEdicion ? 'Aviso actualizado' : 'Aviso publicado exitosamente',
        showConfirmButton: false, timer: 2500
      });
      cancelar(); // Limpia el formulario y avisa al padre
      emit('actualizar-lista'); // Pide al padre que recargue la tabla
    }
  } catch (error) {
    console.error(error);
    Swal.fire({ title: 'Error', text: 'No se pudo guardar el aviso.', icon: 'error', confirmButtonColor: '#0f4c5c' });
  } finally {
    loading.value = false;
  }
};
</script>