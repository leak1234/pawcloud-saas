<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content shadow-lg border-0 rounded-4 overflow-hidden">
        <div class="modal-header bg-white border-bottom-0 pt-4 px-4 pb-2">
          <h5 class="modal-title fw-bold text-dark">➕ Asociar Paciente a {{ dueno?.nombre_completo }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <form @submit.prevent="guardar">
          <div class="modal-body modal-fondo-gris px-4 py-4">
            <div class="bg-white p-4 rounded-3 border shadow-sm">
              <h6 class="fw-bold text-primary mb-3 border-bottom pb-1 small">1. Bio Biométrica</h6>
              <div class="row g-2 mb-3">
                <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Nombre *</label><input type="text" class="form-control" v-model="form.nombre" required maxlength="100" placeholder="Ej: Toby" /></div>
                <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Especie *</label><select class="form-select" v-model="form.especie" required><option value="Perro">🐶 Perro</option><option value="Gato">🐱 Gato</option><option value="Ave">🦜 Ave</option><option value="Exótico">🦎 Exótico</option><option value="Otro">Otro</option></select></div>
                <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Raza</label><input type="text" class="form-control" v-model="form.raza" maxlength="50" placeholder="Ej: Bulldog" /></div>
                <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Color / Pelaje</label><input type="text" class="form-control" v-model="form.color_pelaje" maxlength="100" placeholder="Ej: Dorado" /></div>
              </div>

              <h6 class="fw-bold text-info mb-3 border-bottom pb-1 small">2. Genética</h6>
              <div class="row g-2 mb-3 align-items-center bg-light p-2 rounded border">
                <div class="col-md-4"><label class="form-label small fw-bold text-secondary mb-1">Nacimiento</label><input type="date" class="form-control" v-model="form.fecha_nacimiento" /></div>
                <div class="col-md-3"><label class="form-label small fw-bold text-secondary mb-1">Género *</label><select class="form-select" v-model="form.genero"><option value="Macho">Macho</option><option value="Hembra">Hembra</option></select></div>
                <div class="col-md-2"><label class="form-label small fw-bold text-secondary mb-1">Peso(Kg)</label><input type="number" step="0.01" min="0" @keydown="bloquearTeclasNumericas" @input="limitarLongitud($event, 6)" class="form-control" v-model="form.peso" placeholder="0" /></div>
                <div class="col-md-3 pt-3"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" id="estNewComp" v-model="form.esterilizado"><label class="form-check-label fw-bold small" for="estNewComp">✂️ Castrado</label></div></div>
              </div>

              <h6 class="fw-bold text-danger mb-2 border-bottom pb-1 small">3. Alertas Clínicas</h6>
              <div class="row g-2">
                <div class="col-md-12"><label class="form-label small fw-bold text-secondary mb-1">Temperamento *</label><select class="form-select fw-bold" v-model="form.temperamento"><option value="Dócil">🟢 Dócil</option><option value="Nervioso">🟡 Nervioso</option><option value="Agresivo">🔴 Agresivo</option></select></div>
                <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Alergias</label><textarea class="form-control border-warning" rows="1" v-model="form.alergias_conocidas"></textarea></div>
                <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Patologías</label><textarea class="form-control border-danger" rows="1" v-model="form.patologias_cronicas"></textarea></div>
              </div>
            </div>
          </div>
          <div class="modal-footer bg-white border-top-0 px-4 py-3"><button type="button" class="btn btn-outline-secondary fw-bold rounded-pill px-4" @click="$emit('close')">Cancelar</button><button type="submit" class="btn btn-primary fw-bold rounded-pill px-4 shadow-sm">Guardar Ficha</button></div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import Swal from 'sweetalert2';

const props = defineProps({ show: Boolean, dueno: Object });
const emit = defineEmits(['close', 'guardado']);
const clinicaId = sessionStorage.getItem('clinica_id');

const form = ref({ nombre: '', especie: 'Perro', raza: '', color_pelaje: '', fecha_nacimiento: '', genero: 'Macho', esterilizado: false, peso: '', temperamento: 'Dócil', alergias_conocidas: '', patologias_cronicas: '' });

watch(() => props.show, (isOpen) => {
  if (isOpen) form.value = { nombre: '', especie: 'Perro', raza: '', color_pelaje: '', fecha_nacimiento: '', genero: 'Macho', esterilizado: false, peso: '', temperamento: 'Dócil', alergias_conocidas: '', patologias_cronicas: '' };
});

const bloquearTeclasNumericas = (e) => { if (['e', 'E', '-', '+'].includes(e.key)) e.preventDefault(); };
const limitarLongitud = (e, max) => { if (e.target.value.length > max) e.target.value = e.target.value.slice(0, max); };

const guardar = async () => {
  const r = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/duenos/${props.dueno.id}/mascotas`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form.value)
  });
  if (r.ok) {
    Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Paciente vinculado', showConfirmButton: false, timer: 2000 });
    emit('guardado');
  }
};
</script>

<style scoped>
.modal-fondo-gris { background-color: #f4f6f8; }
input[type=number]::-webkit-inner-spin-button, input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
input[type=number] { -moz-appearance: textfield; appearance: textfield; }
</style>