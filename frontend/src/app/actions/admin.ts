'use server'

import apiClient from '../../libs/apiClient'

export async function getUsers() {
  try {
    const response = await apiClient.get('/admin/users')
    return response.data
  } catch (error) {
    console.error('Error al obtener la lista de usuarios:', error)
    return []
  }
}

export async function deleteUser(userId: number) {
  try {
    const response = await apiClient.delete(`/admin/delete_user/${userId}`)
    return response.data
  } catch (error) {
    console.error('Error al eliminar usuario:', error)
    return { success: false, message: 'Error al eliminar usuario' }
  }
}

export async function changeUserPassword(userId: number, newPassword: string) {
  try {
    const response = await apiClient.post(`/admin/change_password/${userId}`, { newPassword })
    return response.data
  } catch (error) {
    console.error('Error al cambiar la contraseña del usuario:', error)
    return { success: false, message: 'Error al cambiar la contraseña del usuario' }
  }
}

export async function resetUserPassword(userId: number) {
  try {
    const response = await apiClient.post(`/admin/reset_password/${userId}`)
    return response.data
  } catch (error) {
    console.error('Error al resetear la contraseña del usuario:', error)
    return { success: false, message: 'Error al resetear la contraseña del usuario' }
  }
}

export async function registerUser(username: string, password: string) {
  try {
    const response = await apiClient.post('/admin/register', { username, password })
    return response.data
  } catch (error) {
    console.error('Error al registrar nuevo usuario:', error)
    return { success: false, message: 'Error al registrar nuevo usuario' }
  }
}

