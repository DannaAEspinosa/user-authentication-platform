/* eslint-disable @typescript-eslint/no-explicit-any */
'use server'

import { cookies } from 'next/headers'
import apiClient from '../../libs/apiClient'; 

export async function login(prevState: any, formData: FormData) {
  const username = formData.get('username') as string
  const password = formData.get('password') as string

  try {
    const response = await apiClient.post('/auth/login', { username, password })
    if (response.data.success) {
       (await cookies()).set('session', response.data.token, { 
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax'
      })
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
    const cookieStore = cookies()
    const sessionCookie = (await cookieStore).get('session')
    
    if (!sessionCookie) {
      throw new Error('No session cookie found')
    }

    const response = await apiClient.get('/auth/user-info', {
      headers: {
        Cookie: `session=${sessionCookie.value}`
      }
    });
    
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

