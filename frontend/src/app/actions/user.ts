'use server'

import apiClient from '../../libs/apiClient'

export async function changePassword(newPassword: string) {
  try {
    const response = await apiClient.post('/auth/change_password', { new_password: newPassword })
    return response.data
  } catch (error) {
    console.error('Error al cambiar la contraseña:', error)
    return { success: false, message: 'Error al cambiar la contraseña' }
  }
}

