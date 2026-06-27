import { ref } from 'vue';
import Swal from 'sweetalert2';

export function useWhatsapp() {
  const enviando = ref(false);

  // 1. FUNCIÓN ENVIAR MENSAJE
  const enviarMensaje = async (telefono, mensaje) => {
    const clinicaId = sessionStorage.getItem('clinica_id');
    
    if (!clinicaId) {
      Swal.fire('Error', 'No se identificó la sesión activa de la clínica.', 'error');
      return false;
    }

    enviando.value = true;

    // Alerta discreta en la esquina superior derecha
    Swal.fire({
      toast: true,
      position: 'top-end',
      title: 'Despachando WhatsApp...',
      showConfirmButton: false,
      didOpen: () => { Swal.showLoading(); }
    });

    try {
      const respuesta = await fetch(`http://localhost:5000/api/whatsapp/instancia/${clinicaId}/enviar-manual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telefono: telefono,
          mensaje: mensaje
        })
      });

      const data = await respuesta.json();

      if (respuesta.ok) {
        Swal.fire({
          toast: true,
          position: 'top-end',
          icon: 'success',
          title: 'Mensaje enviado al cliente',
          showConfirmButton: false,
          timer: 2000
        });
        return true;
      } else {
        Swal.fire('Atención', data.error || 'No se pudo enviar. Verifica tu conexión en Configuración.', 'warning');
        return false;
      }
    } catch (error) {
      console.error('Error de red:', error);
      Swal.fire('Error de Conexión', 'No hay respuesta del microservicio de mensajería.', 'error');
      return false;
    } finally {
      enviando.value = false;
    }
  };

  // 2. FUNCIÓN DESVINCULAR
  const desvincularWhatsapp = async () => {
    const clinicaId = sessionStorage.getItem('clinica_id');
    
    try {
      const respuesta = await fetch(`http://localhost:5000/api/whatsapp/instancia/${clinicaId}/logout`, {
        method: 'POST'
      });

      if (respuesta.ok) {
        Swal.fire('Desconectado', 'La sesión de WhatsApp ha sido cerrada.', 'success');
        return true;
      }
    } catch (error) {
      Swal.fire('Error', 'No se pudo comunicar con el servidor.', 'error');
    }
    return false;
  };

  // 3. UN SOLO RETURN AL FINAL DE LA FUNCIÓN PRINCIPAL
  return { enviando, enviarMensaje, desvincularWhatsapp }; 
}