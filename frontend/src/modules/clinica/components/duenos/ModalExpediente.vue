<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.7);">
    <div class="modal-dialog modal-xl modal-dialog-scrollable">
      <div class="modal-content shadow-lg border-0 rounded-4 overflow-hidden">
        
        <div class="modal-header bg-dark text-white py-3 px-4 border-0">
          <div>
            <div class="d-flex align-items-center gap-2">
              <h3 class="fw-bold mb-0 text-info">🩺 {{ mascota?.nombre }}</h3>
              <span class="badge bg-light text-dark fs-6">{{ mascota?.edad_calculada || 'Edad Pendiente' }}</span>
              <span v-if="mascota?.esterilizado" class="badge bg-success fs-6">✂️ Esterilizado</span>
              <span v-if="mascota?.temperamento !== 'Dócil'" class="badge bg-danger fs-6">⚠️ {{ mascota?.temperamento }}</span>
            </div>
            <small class="text-secondary fw-semibold mt-1 d-block">Propietario: {{ dueno?.nombre_completo }} | 📞 {{ dueno?.telefono }}</small>
          </div>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>

        <div class="bg-white px-4 pt-2 border-bottom shadow-sm">
          <ul class="nav nav-tabs border-bottom-0 gap-3">
            <li><a class="nav-link fw-bold border-0 px-1 pb-3" :class="tab === 'historial' ? 'active text-info border-bottom border-info border-3' : 'text-secondary'" href="#" @click.prevent="tab = 'historial'">🗓️ Historial Médico</a></li>
            <li><a class="nav-link fw-bold border-0 px-1 pb-3" :class="tab === 'nueva_consulta' ? 'active text-primary border-bottom border-primary border-3' : 'text-secondary'" href="#" @click.prevent="tab = 'nueva_consulta'">✍️ Registrar Consulta</a></li>
            <li><a class="nav-link fw-bold border-0 px-1 pb-3" :class="tab === 'editar' ? 'active text-warning border-bottom border-warning border-3' : 'text-secondary'" href="#" @click.prevent="tab = 'editar'">⚙️ Ficha Clínica</a></li>
          </ul>
        </div>

        <div class="modal-body p-0 modal-fondo-gris">
          <div v-if="tab === 'historial'" class="p-4">
            <div v-if="consultas.length === 0" class="text-center text-muted py-5 bg-white rounded border">No registra atenciones previas.</div>
            <div v-for="c in consultas" :key="c.id" class="card shadow-sm border-0 border-start border-4 mb-3 rounded-3" :class="c.estado === 'pendiente' ? 'border-warning' : 'border-info'">
              <div class="card-body py-3 px-4">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <span class="text-secondary fw-bold small">📅 {{ c.fecha_consulta }}</span>
                  <div>
                    <span class="badge bg-primary bg-opacity-10 text-primary border border-primary px-2 py-1 mx-1">{{ c.servicio_nombre }}</span>
                    <span class="badge px-2 py-1" :class="c.estado === 'pendiente' ? 'bg-warning text-dark' : 'bg-success text-white'">{{ c.estado.toUpperCase() }}</span>
                  </div>
                </div>
                <h5 class="fw-bold text-dark mb-1">{{ c.motivo }}</h5>
                <button class="btn btn-sm btn-outline-info fw-bold rounded-pill mt-2 px-4" @click="verDetalle(c)">👁️ Ver Receta</button>
              </div>
            </div>
          </div>

          <div v-if="tab === 'nueva_consulta'" class="p-4">
            <div class="bg-white p-4 rounded border shadow-sm">
              <form @submit.prevent="guardarConsulta">
                <div class="row g-3 mb-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-secondary mb-1">Servicio *</label>
                    <div class="input-group">
                      <select class="form-select" v-model="formC.servicio_id" required><option v-for="s in serviciosLista" :key="s.id" :value="s.id">{{ s.nombre }}</option></select>
                      <button class="btn btn-primary" type="button" @click="crearSrv">+</button>
                    </div>
                  </div>
                  <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Motivo / Síntoma *</label><input type="text" class="form-control" v-model="formC.motivo" required maxlength="255" /></div>
                </div>

                <div class="row g-3 mb-3 bg-light p-2 rounded border">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-primary mb-1">📅 Programar Cita Futura (Opcional)</label>
                    <input type="datetime-local" class="form-control border-primary" v-model="formC.fecha_programada" :min="minFechaHoraActual" />
                  </div>
                  <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Estatus</label><select class="form-select fw-bold" v-model="formC.estado" :class="formC.estado==='pendiente'?'bg-warning-subtle text-warning-emphasis':'text-success'"><option value="completada">✅ Realizada hoy</option><option value="pendiente">⏳ CITA FUTURA (Pendiente)</option></select></div>
                </div>

                <div class="row g-3 mb-3" v-if="formC.estado === 'completada'">
                  <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Peso (Kg)</label><input type="number" step="0.01" min="0" @keydown="bloquearTeclasNumericas" @input="limitarLongitud($event,6)" class="form-control" v-model="formC.peso_actual" placeholder="0.00" /></div>
                  <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Temp (°C)</label><input type="number" step="0.1" min="0" @keydown="bloquearTeclasNumericas" @input="limitarLongitud($event,5)" class="form-control" v-model="formC.temperatura" placeholder="0.0" /></div>
                </div>
                <div class="mb-3" v-if="formC.estado === 'completada'"><label class="form-label small fw-bold text-secondary mb-1">Diagnóstico</label><input type="text" class="form-control mb-2" v-model="formC.diagnostico" maxlength="500" /><textarea class="form-control" rows="2" v-model="formC.sintomas" placeholder="Anamnesis"></textarea></div>
                <div class="mb-4" v-if="formC.estado === 'completada'"><label class="form-label small fw-bold text-success mb-1">Receta 💊</label><textarea class="form-control border-success" rows="3" v-model="formC.tratamiento_receta"></textarea></div>
                <div class="d-flex justify-content-end border-top pt-3"><button type="submit" class="btn btn-primary fw-bold px-5 rounded-pill" :disabled="loading">Guardar Expediente</button></div>
              </form>
            </div>
          </div>

          <div v-if="tab === 'editar'" class="p-4">
            <div class="bg-white p-4 rounded border shadow-sm">
              <form @submit.prevent="guardarBio">
                <h6 class="fw-bold text-primary mb-3 border-bottom pb-2">🐾 1. Identificación</h6>
                <div class="row g-3 mb-4">
                  <div class="col-md-3"><label class="form-label small fw-bold text-secondary mb-1">Nombre *</label><input type="text" class="form-control fw-bold text-primary" v-model="formE.nombre" required maxlength="100" /></div>
                  <div class="col-md-3"><label class="form-label small fw-bold text-secondary mb-1">Especie *</label><select class="form-select" v-model="formE.especie" required><option value="Perro">🐶 Perro</option><option value="Gato">🐱 Gato</option><option value="Ave">🦜 Ave</option><option value="Exótico">🦎 Exótico</option><option value="Otro">Otro</option></select></div>
                  <div class="col-md-3"><label class="form-label small fw-bold text-secondary mb-1">Raza</label><input type="text" class="form-control" v-model="formE.raza" maxlength="50" /></div>
                  <div class="col-md-3"><label class="form-label small fw-bold text-secondary mb-1">Color</label><input type="text" class="form-control" v-model="formE.color_pelaje" maxlength="100" /></div>
                </div>

                <h6 class="fw-bold text-info mb-3 border-bottom pb-2">🧬 2. Biometría</h6>
                <div class="row g-3 mb-4 align-items-center bg-light p-2 rounded border">
                  <div class="col-md-3"><label class="form-label small fw-bold text-secondary mb-1">Nacimiento</label><input type="date" class="form-control border-info" v-model="formE.fecha_nacimiento" /></div>
                  <div class="col-md-3"><label class="form-label small fw-bold text-secondary mb-1">Género *</label><select class="form-select" v-model="formE.genero" required><option value="Macho">Macho</option><option value="Hembra">Hembra</option></select></div>
                  <div class="col-md-3"><label class="form-label small fw-bold text-secondary mb-1">Peso (Kg)</label><input type="number" step="0.01" min="0" @keydown="bloquearTeclasNumericas" @input="limitarLongitud($event,6)" class="form-control" v-model="formE.peso" /></div>
                  <div class="col-md-3 pt-3"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" id="estEditC" v-model="formE.esterilizado"><label class="form-check-label fw-bold small" for="estEditC">✂️ Castrado</label></div></div>
                </div>

                <h6 class="fw-bold text-danger mb-3 border-bottom pb-2">⚠️ 3. Alertas</h6>
                <div class="row g-3 mb-2">
                  <div class="col-md-12"><label class="form-label small fw-bold text-secondary mb-1">Temperamento *</label><select class="form-select fw-bold" v-model="formE.temperamento"><option value="Dócil">🟢 Dócil</option><option value="Nervioso">🟡 Nervioso</option><option value="Agresivo">🔴 Agresivo</option></select></div>
                  <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Alergias</label><textarea class="form-control border-warning" rows="2" v-model="formE.alergias_conocidas"></textarea></div>
                  <div class="col-md-6"><label class="form-label small fw-bold text-secondary mb-1">Patologías</label><textarea class="form-control border-danger" rows="2" v-model="formE.patologias_cronicas"></textarea></div>
                </div>
                <div class="d-flex justify-content-end border-top pt-4 mt-4"><button type="submit" class="btn btn-warning text-dark fw-bold px-5 rounded-pill shadow-sm">💾 Actualizar Ficha</button></div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import Swal from 'sweetalert2';

const props = defineProps({ show: Boolean, mascota: Object, dueno: Object, serviciosLista: Array });
const emit = defineEmits(['close', 'actualizado', 'recargar-servicios']);

const clinicaId = sessionStorage.getItem('clinica_id');
const veteId = sessionStorage.getItem('usuario_id') || 1;

const tab = ref('historial');
const loading = ref(false);
const consultas = ref([]);

const minFechaHoraActual = ref('');

const formC = ref({ servicio_id: '', motivo: '', sintomas: '', diagnostico: '', tratamiento_receta: '', peso_actual: '', temperatura: '', fecha_programada: '', estado: 'completada' });
const formE = ref({ nombre: '', especie: 'Perro', raza: '', color_pelaje: '', fecha_nacimiento: '', genero: 'Macho', esterilizado: false, peso: '', temperamento: 'Dócil', alergias_conocidas: '', patologias_cronicas: '' });

// Obtener la hora actual en formato ISO local para bloquear el calendario html5
const actualizarMinFechaHora = () => {
  const tzOffset = (new Date()).getTimezoneOffset() * 60000;
  minFechaHoraActual.value = (new Date(Date.now() - tzOffset)).toISOString().slice(0, 16);
};

watch(() => props.show, async (isOpen) => {
  if (isOpen && props.mascota) {
    actualizarMinFechaHora();
    tab.value = 'historial';
    formC.value = { servicio_id: '', motivo: '', sintomas: '', diagnostico: '', tratamiento_receta: '', peso_actual: '', temperatura: '', fecha_programada: '', estado: 'completada' };
    formE.value = { 
      nombre: props.mascota.nombre, especie: props.mascota.especie, raza: props.mascota.raza || '', color_pelaje: props.mascota.color_pelaje || '', 
      fecha_nacimiento: props.mascota.fecha_nacimiento || '', genero: props.mascota.genero, esterilizado: props.mascota.esterilizado || false, 
      peso: props.mascota.peso || '', temperamento: props.mascota.temperamento || 'Dócil', alergias_conocidas: props.mascota.alergias_conocidas || '', patologias_cronicas: props.mascota.patologias_cronicas || '' 
    };
    await cargarTimeline();
  }
});

watch(() => formC.value.fecha_programada, (f) => {
  formC.value.estado = f && new Date(f).getTime() > Date.now() ? 'pendiente' : 'completada';
});

const bloquearTeclasNumericas = (e) => { if (['e', 'E', '-', '+'].includes(e.key)) e.preventDefault(); };
const limitarLongitud = (e, max) => { if (e.target.value.length > max) e.target.value = e.target.value.slice(0, max); };

const cargarTimeline = async () => {
  const r = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/mascotas/${props.mascota.id}/consultas`);
  if (r.ok) consultas.value = await r.json();
};

const crearSrv = async () => {
  const { value: val } = await Swal.fire({
    title: '🏷️ Nuevo Servicio', html: '<input id="s1" class="form-control mb-2" placeholder="Nombre"><input id="s2" type="number" class="form-control" placeholder="Precio">',
    showCancelButton: true, preConfirm: () => ({ nombre: document.getElementById('s1').value, precio_base: parseFloat(document.getElementById('s2').value) || 0 })
  });
  if (val?.nombre) {
    await fetch(`http://localhost:5000/api/clinica/${clinicaId}/servicios`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(val) });
    emit('recargar-servicios');
  }
};

const guardarConsulta = async () => {
  // BLOQUEO LÓGICO DE SEGURIDAD PARA CITAS FUTURAS
  if (formC.value.fecha_programada) {
    const fechaElegida = new Date(formC.value.fecha_programada);
    const ahora = new Date();
    const hora = fechaElegida.getHours();

    // 1. Validar que la fecha/hora no sea del pasado (por si burlaron el HTML5)
    if (fechaElegida < ahora) {
      Swal.fire('Atención', 'No puedes agendar una cita en una hora pasada.', 'warning');
      return;
    }

    // 2. Validar que esté en horario de atención (08:00 a.m. a 08:00 p.m.)
    if (hora < 8 || hora >= 20) {
      Swal.fire({
        title: 'Horario Inválido',
        text: 'La clínica no opera de madrugada. Las citas deben programarse entre las 08:00 a.m. y las 08:00 p.m.',
        icon: 'error',
        confirmButtonColor: '#0f4c5c'
      });
      return; // Detenemos la ejecución aquí, no se guarda en BD
    }
  }

  loading.value = true;
  const r = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/mascotas/${props.mascota.id}/consultas`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...formC.value, veterinario_id: veteId })
  });
  if (r.ok) {
    Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Guardado', showConfirmButton: false, timer: 1500 });
    await cargarTimeline();
    tab.value = 'historial';
    emit('actualizado');

    if (r.ok) {
      Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Guardado', showConfirmButton: false, timer: 1500 });
      await cargarTimeline();
      tab.value = 'historial';
      emit('actualizado');
      
      // 🔥 LA MAGIA: Damos un "grito global" a toda la aplicación
      window.dispatchEvent(new Event('clinica-actualizada'));
      
    } else {
      Swal.fire('Error', 'No se pudo guardar la consulta.', 'error');
    }
  }
  loading.value = false;
};

const guardarBio = async () => {
  const r = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/mascotas/${props.mascota.id}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formE.value)
  });
  if (r.ok) {
    Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Ficha médica actualizada', showConfirmButton: false, timer: 1500 });
    emit('actualizado');
  }
};

const verDetalle = (c) => Swal.fire({ title: 'Receta', html: `<div class="text-start small"><b>Diagnóstico:</b> ${c.diagnostico||'N/A'}<hr><pre>${c.tratamiento_receta||'Sin indicaciones'}</pre></div>` });
</script>

<style scoped>
.modal-fondo-gris { background-color: #f4f6f8; }
input[type=number]::-webkit-inner-spin-button, input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
input[type=number] { -moz-appearance: textfield; appearance: textfield; }
</style>