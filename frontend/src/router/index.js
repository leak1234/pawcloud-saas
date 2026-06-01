import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../modules/saas_admin/views/LoginView.vue'

// Importamos el Layout base
import SaasLayout from '../core/layouts/SaasLayout.vue'

// Importamos las Vistas (Las "habitaciones")
import DashboardView from '../modules/saas_admin/views/DashboardView.vue'
import ClinicasView from '../modules/saas_admin/views/ClinicasView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { 
      path: '/', 
      name: 'login', 
      component: LoginView 
    },
    {
      // RUTA PADRE: El Layout con el menú lateral
      path: '/saas-global',
      component: SaasLayout,
      children: [
        {
          path: '', // Al entrar a /saas-global, carga el Dashboard
          name: 'saas-dashboard',
          component: DashboardView
        },
        {
          path: 'clinicas', // Al entrar a /saas-global/clinicas, carga la tabla
          name: 'saas-clinicas',
          component: ClinicasView
        }
      ]
    }
  ]
})

export default router