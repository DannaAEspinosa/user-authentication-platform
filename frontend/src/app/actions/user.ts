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
    return { success: true, message: response.data.message }
  } catch (error: any) {
    console.error('Error al cambiar la contraseña:', error)
    return { 
      success: false, 
      message: error.response?.data?.message || 'Error al cambiar la contraseña'
    }
  }
}