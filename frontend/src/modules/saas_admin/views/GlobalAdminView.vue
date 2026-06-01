<template>
  <div class="layout-admin">
    <aside class="sidebar">
      <div class="logo-container">
        <h2>🛠️ PawCloud Admin</h2>
        <p class="rol-badge">Súper Administrador</p>
      </div>

      <nav class="menu">
        <button :class="{ activo: vistaActual === 'dashboard' }" @click="vistaActual = 'dashboard'">
          🏠 Dashboard
        </button>
        <button :class="{ activo: vistaActual === 'clinicas' }" @click="vistaActual = 'clinicas'">
          🏥 Gestión de Clínicas
        </button>
        <button :class="{ activo: vistaActual === 'planes' }" @click="vistaActual = 'planes'">
          💳 Planes y Pagos
        </button>
        <button :class="{ activo: vistaActual === 'equipo' }" @click="vistaActual = 'equipo'">
          👥 Equipo Interno
        </button>
      </nav>

      <div class="sidebar-footer">
        <button class="btn-salir" @click="cerrarSesion">Cerrar Sesión</button>
      </div>
    </aside>

    <main class="contenido-principal">
      
      <section v-if="vistaActual === 'dashboard'" class="vista">
        <h1>Resumen del Sistema</h1>
        <div class="kpi-grid">
          <div class="tarjeta-kpi">
            <h3>Total Clínicas</h3>
            <p class="numero">1</p>
          </div>
          <div class="tarjeta-kpi">
            <h3>Clínicas Activas</h3>
            <p class="numero verde">1</p>
          </div>
          <div class="tarjeta-kpi">
            <h3>Suspendidas</h3>
            <p class="numero rojo">0</p>
          </div>
        </div>
      </section>

      <section v-if="vistaActual === 'clinicas'" class="vista">
        <div class="cabecera-vista">
          <h1>Gestión de Clínicas</h1>
          <button class="btn-primario">+ Nueva Clínica</button>
        </div>

        <div class="tabla-contenedor">
          <table class="tabla-datos">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre del Negocio</th>
                <th>Correo Administrador</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1</td>
                <td>Veterinaria Huellas</td>
                <td>vet@huellas.com</td>
                <td>
                  <span class="badge" :class="clinicaActiva ? 'badge-activo' : 'badge-inactivo'">
                    {{ clinicaActiva ? 'Activa' : 'Suspendida' }}
                  </span>
                </td>
                <td>
                  <button 
                    class="btn-accion" 
                    :class="clinicaActiva ? 'btn-peligro' : 'btn-exito'"
                    @click="cambiarEstadoClinica">
                    {{ clinicaActiva ? 'Suspender' : 'Reactivar' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="vistaActual === 'planes'" class="vista">
        <h1>Planes y Suscripciones</h1>
        <p>Aquí configuraremos los límites de mascotas por plan.</p>
      </section>

      <section v-if="vistaActual === 'equipo'" class="vista">
        <h1>Equipo PawCloud</h1>
        <p>Gestión de accesos para Nicolas, Juan Josue, James, etc.</p>
      </section>

    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Control de navegación interna
const vistaActual = ref('dashboard');

// Simulación del estado de la clínica (Soft Delete)
const clinicaActiva = ref(true);

const cambiarEstadoClinica = () => {
  // Aquí luego conectaremos con axios a Flask para cambiar el 'activo = False' en PostgreSQL
  clinicaActiva.value = !clinicaActiva.value;
  alert(clinicaActiva.value ? 'Clínica reactivada con éxito.' : '¡Clínica suspendida! El cliente ya no podrá iniciar sesión.');
};

const cerrarSesion = () => {
  localStorage.clear();
  router.push('/');
};
</script>

<style scoped>
/* ESTRUCTURA BASE */
.layout-admin {
  display: flex;
  height: 100vh;
  background-color: #f1f5f9;
}

/* BARRA LATERAL */
.sidebar {
  width: 260px;
  background-color: #1e293b;
  color: white;
  display: flex;
  flex-direction: column;
}
.logo-container {
  padding: 20px;
  border-bottom: 1px solid #334155;
  text-align: center;
}
.rol-badge {
  font-size: 12px;
  background: #3b82f6;
  padding: 4px 8px;
  border-radius: 12px;
  display: inline-block;
  margin-top: 5px;
}
.menu {
  flex-grow: 1;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.menu button {
  background: none;
  border: none;
  color: #cbd5e1;
  text-align: left;
  padding: 15px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: 0.2s;
}
.menu button:hover, .menu button.activo {
  background-color: #334155;
  color: white;
  border-left: 4px solid #3b82f6;
}
.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #334155;
}
.btn-salir {
  width: 100%;
  padding: 10px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

/* CONTENIDO PRINCIPAL */
.contenido-principal {
  flex-grow: 1;
  padding: 40px;
  overflow-y: auto;
}
.cabecera-vista {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

/* TARJETAS KPI */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}
.tarjeta-kpi {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border-left: 4px solid #3b82f6;
}
.numero { font-size: 32px; font-weight: bold; margin-top: 10px; color: #1e293b; }
.verde { color: #10b981; }
.rojo { color: #ef4444; }

/* TABLAS */
.tabla-contenedor {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.tabla-datos {
  width: 100%;
  border-collapse: collapse;
}
.tabla-datos th, .tabla-datos td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}
.tabla-datos th { background: #f8fafc; color: #475569; }

/* BADGES Y BOTONES */
.badge { padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
.badge-activo { background: #d1fae5; color: #065f46; }
.badge-inactivo { background: #fee2e2; color: #991b1b; }

.btn-primario { background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.btn-accion { padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; color: white; }
.btn-peligro { background: #ef4444; }
.btn-exito { background: #10b981; }
</style>