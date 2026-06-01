<template>
  <div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="text-dark fw-bold fs-3">Gestión de Clínicas</h1>
      <button class="btn btn-primary fw-bold shadow-sm" @click="abrirModalCrear">
        + Nueva Clínica
      </button>
    </div>

    <div class="card shadow-sm border-0 mb-3 bg-light">
      <div class="card-body py-3">
        <div class="row g-2">
          <div class="col-md-8">
            <input 
              type="text" 
              class="form-control border-secondary-subtle" 
              placeholder="🔍 Buscar por negocio, administrador o correo..." 
              v-model="filtroTexto"
            />
          </div>
          <div class="col-md-4">
            <select class="form-select border-secondary-subtle fw-semibold" v-model="filtroEstado">
              <option value="activos">🟢 Solo Clínicas Activas</option>
              <option value="inactivos">🔴 Solo Clínicas Suspendidas</option>
              <option value="todos">⚪ Mostrar Todas</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-body p-0 table-responsive">
        <table class="table table-hover table-striped mb-0 align-middle">
          <thead class="table-dark">
            <tr>
              <th class="ps-3">ID</th>
              <th>Negocio</th>
              <th>NIT</th>
              <th>Dirección Física</th>
              <th>Administrador</th>
              <th>Correo Electrónico</th>
              <th>Estado</th>
              <th class="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="clinica in clinicasFiltradas" :key="clinica.id">
              <td class="ps-3">{{ clinica.id }}</td>
              <td class="fw-bold text-dark">{{ clinica.nombre_negocio }}</td>
              <td>{{ clinica.nit }}</td>
              <td>{{ clinica.direccion }}</td>
              <td>{{ clinica.nombre_usuario }}</td>
              <td>{{ clinica.email }}</td>
              <td>
                <span class="badge" :class="clinica.activo ? 'bg-success' : 'bg-danger'">
                  {{ clinica.activo ? 'Activa' : 'Suspendida' }}
                </span>
              </td>
              <td class="text-center">
                <div class="d-flex justify-content-center gap-2">
                  <button class="btn btn-warning btn-sm text-dark fw-bold" @click="abrirModalEditar(clinica)">
                    ✏️ Editar
                  </button>
                  <button 
                    class="btn btn-sm fw-bold text-white" 
                    :class="clinica.activo ? 'btn-danger' : 'btn-success'"
                    @click="alternarEstado(clinica)"
                    style="width: 90px;">
                    {{ clinica.activo ? 'Suspender' : 'Reactivar' }}
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="clinicasFiltradas.length === 0">
              <td colspan="8" class="text-center text-muted py-4">
                No se encontraron clínicas que coincidan con los filtros.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="mostrarModal" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content shadow-lg border-0">
          
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold text-dark">
              {{ editandoId ? 'Editar Clínica' : 'Registrar Nueva Clínica' }}
            </h5>
            <button type="button" class="btn-close" @click="cerrarModal"></button>
          </div>

          <form @submit.prevent="guardarClinica">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary small">Nombre del Negocio:</label>
                <input type="text" class="form-control" v-model="nuevaClinica.nombre_negocio" required />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary small">NIT (Opcional):</label>
                <input type="text" class="form-control" v-model="nuevaClinica.nit" />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary small">Dirección Física:</label>
                <input type="text" class="form-control" v-model="nuevaClinica.direccion" required />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary small">Veterinario Administrador:</label>
                <input type="text" class="form-control" v-model="nuevaClinica.nombre_usuario" required />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary small">Correo Electrónico:</label>
                <input type="email" class="form-control" v-model="nuevaClinica.email" required />
              </div>
              <div class="mb-1">
                <label class="form-label fw-semibold text-secondary small">
                  Contraseña {{ editandoId ? '(Dejar vacío para no cambiar)' : '' }}:
                </label>
                <input type="password" class="form-control" v-model="nuevaClinica.password" :required="!editandoId" />
              </div>
            </div>

            <div class="modal-footer bg-light border-0">
              <button type="button" class="btn btn-secondary fw-bold" @click="cerrarModal">Cancelar</button>
              <button type="submit" class="btn btn-success fw-bold">
                {{ editandoId ? 'Guardar Cambios' : 'Registrar' }}
              </button>
            </div>
          </form>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// IMPORTANTE: Importamos 'computed' de vue
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const listaClinicas = ref([]);
const mostrarModal = ref(false);
const editandoId = ref(null);

// NUEVO: Variables reactivas para los filtros
const filtroTexto = ref('');
const filtroEstado = ref('activos'); // Valor por defecto

const nuevaClinica = ref({
  nombre_negocio: '', nit: '', direccion: '', nombre_usuario: '', email: '', password: '', rol: 'admin'
});

// NUEVO: La propiedad computada que hace la magia de filtrar
const clinicasFiltradas = computed(() => {
  return listaClinicas.value.filter(clinica => {
    // 1. Filtrar por el Dropdown (Estado)
    let pasaEstado = true;
    if (filtroEstado.value === 'activos') {
      pasaEstado = clinica.activo === true;
    } else if (filtroEstado.value === 'inactivos') {
      pasaEstado = clinica.activo === false;
    }

    // 2. Filtrar por la Barra de Búsqueda (Texto)
    const termino = filtroTexto.value.toLowerCase();
    const pasaTexto = 
      clinica.nombre_negocio.toLowerCase().includes(termino) ||
      clinica.nombre_usuario.toLowerCase().includes(termino) ||
      clinica.email.toLowerCase().includes(termino);

    // Retorna true solo si cumple ambas condiciones
    return pasaEstado && pasaTexto;
  });
});

const cargarClinicas = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/admin/clinicas');
    listaClinicas.value = res.data;
  } catch (error) {
    console.error("Error al cargar clínicas", error);
  }
};

const abrirModalCrear = () => {
  editandoId.value = null;
  nuevaClinica.value = { nombre_negocio: '', nit: '', direccion: '', nombre_usuario: '', email: '', password: '', rol: 'admin' };
  mostrarModal.value = true;
};

const abrirModalEditar = (clinica) => {
  editandoId.value = clinica.id;
  nuevaClinica.value = {
    nombre_negocio: clinica.nombre_negocio,
    nit: clinica.nit === 'S/N' ? '' : clinica.nit,
    direccion: clinica.direccion === 'Sin dirección' ? '' : clinica.direccion,
    nombre_usuario: clinica.nombre_usuario,
    email: clinica.email,
    password: '',
    rol: 'admin'
  };
  mostrarModal.value = true;
};

const guardarClinica = async () => {
  try {
    const payload = {
      nombre_negocio: nuevaClinica.value.nombre_negocio,
      nit: nuevaClinica.value.nit,
      direccion: nuevaClinica.value.direccion,
      nombre_usuario: nuevaClinica.value.nombre_usuario,
      email: nuevaClinica.value.email,
      password: nuevaClinica.value.password,
      rol: 'admin'
    };

    if (editandoId.value) {
      await axios.put(`http://localhost:5000/api/admin/clinicas/${editandoId.value}`, payload);
      alert('Clínica actualizada con éxito.');
    } else {
      await axios.post('http://localhost:5000/api/admin/registrar', payload);
      alert('Clínica registrada correctamente.');
    }
    cerrarModal();
    cargarClinicas();
  } catch (error) {
    alert(error.response?.data?.error || 'Error al procesar la solicitud');
  }
};

const alternarEstado = async (clinica) => {
  try {
    const res = await axios.post(`http://localhost:5000/api/admin/clinicas/${clinica.id}/cambiar-estado`);
    clinica.activo = res.data.nuevo_estado; 
    // Magia de Vue: Al cambiar el estado, la tabla se actualiza sola y la clínica desaparece de la vista "activos"
  } catch (error) {
    alert('Error al cambiar el estado');
  }
};

const cerrarModal = () => {
  mostrarModal.value = false;
};

onMounted(() => {
  cargarClinicas();
});
</script>

<style scoped>
/* Sin CSS extra. Bootstrap maneja todo */
</style>