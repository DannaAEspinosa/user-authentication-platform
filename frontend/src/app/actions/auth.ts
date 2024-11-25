'use server'

import apiClient from '../../libs/apiClient'
export async function login(prevState: any, formData: FormData) {
  const username = formData.get('username') as string;
  const password = formData.get('password') as string;

  try {
    const response = await apiClient.post('/auth/login', { username, password });
    const data = response.data;

    if (data.success) {
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', data.token);
      }
      return { success: true, message: 'Inicio de sesión exitoso' };
    } else {
      return { success: false, message: data.message || 'Credenciales inválidas' };
    }
  } catch (error) {
    console.error('Error durante el inicio de sesión:', error);
    return { success: false, message: 'Error al intentar iniciar sesión' };
  }
}

export async function getUserInfo() {
  try {
    const response = await apiClient.get('/auth/user-info');
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.status === 401) {
      console.error('Error de autenticación al obtener la información del usuario');
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
      }
      throw new Error('Sesión expirada o inválida');
    }
    console.error('Error al obtener la información del usuario:', error);
    throw error;
  }
}

export async function logout() {
  try {
    await apiClient.post('/auth/logout');
  } catch (error) {
    console.error('Error durante el cierre de sesión:', error);
  } finally {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }
}

