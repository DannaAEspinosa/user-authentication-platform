'use server'

import { cookies } from 'next/headers'
import apiClient from '../../libs/apiClient'

async function getAuthHeaders() {
  const token = (await cookies()).get('token')?.value
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function changePassword(newPassword: string) {
  try {
    const headers = await getAuthHeaders()
    const response = await apiClient.post(
      '/auth/change_password',
      { new_password: newPassword },
      { headers }
    )
    return response.data
  } catch (error: any) {
    console.error('Error al cambiar la contraseña:', error)
    if (error.response?.status === 404) {
      return { 
        success: false, 
        message: 'Ruta no encontrada. Por favor, contacte al administrador.' 
      }
    }
    return { 
      success: false, 
      message: 'Error al cambiar la contraseña. Por favor, intente nuevamente.' 
    }
  }
}

