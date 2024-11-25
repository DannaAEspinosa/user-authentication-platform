'use server'

import { cookies } from 'next/headers'
import apiClient from '../../libs/apiClient'

export async function login(prevState: any, formData: FormData) {
  const username = formData.get('username') as string;
  const password = formData.get('password') as string;

  try {
    const response = await apiClient.post('/auth/login', { username, password });
    const data = response.data;

    if (data.success) {
      (await cookies()).set('token', data.token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 3600 // 1 hour
      });

      return { success: true, message: 'Inicio de sesión exitoso' };
    } else {
      return { success: false, message: data.message || 'Credenciales inválidas' };
    }
  } catch (error: any) {
    console.error('Error durante el inicio de sesión:', error);
    return { 
      success: false, 
      message: error.response?.data?.message || 'Error al intentar iniciar sesión'
    };
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
    console.error('Error al obtener la información del usuario:', error);
    if (error.response?.status === 401) {
      (await cookies()).delete('token');
      throw new Error('Sesión expirada o inválida');
    }
    throw new Error(error.response?.data?.message || 'Error al obtener la información del usuario');
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
  } catch (error: any) {
    console.error('Error durante el cierre de sesión:', error);
  } finally {
    (await cookies()).delete('token');
  }
}

