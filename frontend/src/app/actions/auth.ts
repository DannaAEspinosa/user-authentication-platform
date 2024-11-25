'use server'

import apiClient from '../../libs/apiClient'
import { cookies } from 'next/headers'

export async function login(prevState: any, formData: FormData) {
  const username = formData.get('username') as string;
  const password = formData.get('password') as string;

  try {
    const response = await apiClient.post('/auth/login', { username, password });
    const data = response.data;

    if (data.success) {
      // Store the token in a secure HTTP-only cookie
      (await
        // Store the token in a secure HTTP-only cookie
        cookies()).set('token', data.token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 3600 // 1 hour
      });

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
    const token = (await cookies()).get('token')?.value;
    if (!token) {
      throw new Error('No token found, please login again');
    }

    const response = await apiClient.get('/auth/user-info', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.status === 401) {
      console.error('Error de autenticación al obtener la información del usuario');
      (await cookies()).delete('token');
      throw new Error('Sesión expirada o inválida');
    }
    console.error('Error al obtener la información del usuario:', error);
    throw error;
  }
}

export async function logout() {
  try {
    const token = (await cookies()).get('token')?.value;
    if (token) {
      await apiClient.post('/auth/logout', null, {
        headers: { Authorization: `Bearer ${token}` }
      });
    }
  } catch (error) {
    console.error('Error durante el cierre de sesión:', error);
  } finally {
    (await cookies()).delete('token');
  }
}

