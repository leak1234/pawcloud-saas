import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../modules/saas_admin/views/LoginView.vue'
import SaasLayout from '../core/layouts/SaasLayout.vue'
import SaasDashboardView from '../modules/saas_admin/views/DashboardView.vue' 
import ClinicasView from '../modules/saas_admin/views/ClinicasView.vue'
import PlanesView from '../modules/saas_admin/views/PlanesView.vue'
import ReportesView from '../modules/saas_admin/views/ReportesView.vue'
import Notificaciones from '../modules/saas_admin/views/Notificaciones.vue'

import ClinicaLayout from '../core/layouts/ClinicaLayout.vue' 
import ClinicaDashboardView from '../modules/clinica/views/DashboardView.vue'
import EmpleadosView from '../modules/clinica/views/EmpleadosView.vue'
import DuenosView from '../modules/clinica/views/DuenosView.vue'
import ServiciosView from '../modules/clinica/views/ServiciosView.vue'
import ConfiguracionWhatsappView from '../modules/clinica/views/ConfiguracionWhatsappView.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'login', component: LoginView },
    {
      path: '/saas-global',
      component: SaasLayout,
      children: [
        { path: '', name: 'saas-dashboard', component: SaasDashboardView },
        { path: 'clinicas', name: 'saas-clinicas', component: ClinicasView },
        { path: 'planes', name: 'saas-planes', component: PlanesView },
        { path: 'reportes', name: 'Reportes', component: ReportesView },
        { path: 'notificaciones', name: 'Notificaciones', component: Notificaciones }
      ]
    },
    {
      path: '/clinica',
      component: ClinicaLayout,
      children: [
        { path: 'dashboard', name: 'clinica-dashboard', component: ClinicaDashboardView },
        { path: 'empleados', name: 'clinica-empleados', component: EmpleadosView },
        { path: 'duenos', name: 'clinica-duenos', component: DuenosView },
        { path: 'tarifario', name: 'clinica-tarifario', component: ServiciosView },
        { 
          path: 'whatsapp', 
          name: 'clinica-whatsapp', 
          component: ConfiguracionWhatsappView,
          meta: { requiereAdmin: true } // Mantenemos la protección de seguridad
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const rolActivo = sessionStorage.getItem('rol');

  if (to.path !== '/' && !rolActivo) {
    next({ path: '/', query: { timeout: 'true' } }); 
  } else if (to.path === '/' && rolActivo) {
    if (rolActivo === 'superadmin') {
      next('/saas-global');
    } else {
      next('/clinica/dashboard');
    }
  } else if (to.path === '/clinica/empleados' && rolActivo !== 'admin') {
    next('/clinica/dashboard');
  } else {
    next();
  }
});

export default router;