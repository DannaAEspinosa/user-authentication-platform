/* eslint-disable @typescript-eslint/no-explicit-any */
'use server'

import { cookies } from 'next/headers'
import apiClient from '../../libs/apiClient'; 

export async function login(prevState: any, formData: FormData) {
  const username = formData.get('username') as string
  const password = formData.get('password') as string

  try {
    const response = await apiClient.post('/auth/login', { username, password }, {
      withCredentials: true,  // Asegúrate de incluir las credenciales en la solicitud
    });
    console.log("Reponse login",response)
    if (response.data.success) {
      return { success: true, message: 'Inicio de sesión exitoso' }
    } else {
      return { success: false, message: response.data.message || 'Credenciales inválidas' }
    }
  } catch (error) {
    console.error('Error durante el inicio de sesión:', error)
    return { success: false, message: 'Error al intentar iniciar sesión' }
  }
}

export async function getUserInfo() {
  try {
      const response = await apiClient.get('/auth/user-info', {
        withCredentials: true,
      });
      console.log("Responde GetUser", response)
      return response.data;

  } catch (error) {
      console.error('Error al obtener la información del usuario:', error);
      throw error;
  }
}


export async function logout() {
  try {
    await apiClient.post('/auth/logout')
    ;(await cookies()).delete('session')
  } catch (error) {
    console.error('Error durante el cierre de sesión:', error)
  }
}
