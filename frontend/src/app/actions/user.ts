'use server'

import apiClient from '../../libs/apiClient'; 

export async function changePassword(newPassword: string) {
  try {
    const response = await apiClient.post('/auth/change-password', { newPassword })
    return response.data
  } catch (error) {
    console.error('Error al cambiar la contraseña:', error)
    return { success: false, message: 'Error al cambiar la contraseña' }
  }
}

export async function getLast_Login() {
    try {
      const response = await apiClient.get('/auth/last_login')
      return response.data
    } catch (error) {
      console.error('Error al obtener el ultimo login  ', error)
      return []
    }
  }

