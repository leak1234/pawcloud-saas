import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../modules/saas_admin/views/LoginView.vue'

// ============================================================================
// IMPORTACIONES: SÚPER ADMINISTRADOR (SAAS)
// ============================================================================
import SaasLayout from '../core/layouts/SaasLayout.vue'
import SaasDashboardView from '../modules/saas_admin/views/DashboardView.vue' 
import ClinicasView from '../modules/saas_admin/views/ClinicasView.vue'

// ============================================================================
// IMPORTACIONES: MÓDULO DE LA CLÍNICA (VETERINARIA)
// ============================================================================
// CORRECCIÓN: Apuntamos directamente al archivo .vue
import ClinicaLayout from '../core/layouts/ClinicaLayout.vue' 
import ClinicaDashboardView from '../modules/clinica/views/DashboardView.vue'
import EmpleadosView from '../modules/clinica/views/EmpleadosView.vue'
import DuenosView from '../modules/clinica/views/DuenosView.vue'

// ============================================================================
// CONFIGURACIÓN DE RUTAS
// ============================================================================
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { 
      path: '/', 
      name: 'login', 
      component: LoginView 
    },
    
    // ------------------------------------------------------------------------
    // ZONA 1: SÚPER ADMINISTRADOR
    // ------------------------------------------------------------------------
    {
      path: '/saas-global',
      component: SaasLayout,
      children: [
        {
          path: '', 
          name: 'saas-dashboard',
          component: SaasDashboardView
        },
        {
          path: 'clinicas', 
          name: 'saas-clinicas',
          component: ClinicasView
        }
      ]
    },

    // ------------------------------------------------------------------------
    // ZONA 2: PORTAL DE LA CLÍNICA VETERINARIA
    // ------------------------------------------------------------------------
    {
      path: '/clinica',
      component: ClinicaLayout,
      children: [
        { 
          path: 'dashboard', 
          name: 'clinica-dashboard',
          component: ClinicaDashboardView 
        },
        { 
          path: 'empleados', 
          name: 'clinica-empleados',
          component: EmpleadosView 
        },
        { 
          path: 'clientes', 
          name: 'clinica-clientes',
          component: DuenosView 
        } 
      ]
    }
  ]
})

export default router