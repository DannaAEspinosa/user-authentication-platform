'use server'

import { cookies } from 'next/headers'
import apiClient from '../../libs/apiClient'
async function getAuthHeaders() {
  const token = (await cookies()).get('token')?.value
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function getUsers() {
  try {
    const headers = await getAuthHeaders()
    const response = await apiClient.get('/admin/users', { headers })
    return { success: true, data: response.data }
  } catch (error: any) {
    console.error('Error al obtener la lista de usuarios:', error)
    return { 
      success: false, 
      message: error.response?.data?.message || 'Error al obtener la lista de usuarios'
    }
  }
}

export async function deleteUser(userId: number) {
  try {
    const headers = await getAuthHeaders()
    const response = await apiClient.delete(`/admin/delete_user/${userId}`, { headers })
    return { success: true, message: response.data.message }
  } catch (error: any) {
    console.error('Error al eliminar usuario:', error)
    return { 
      success: false, 
      message: error.response?.data?.message || 'Error al eliminar usuario'
    }
  }
}

export async function changeUserPassword(userId: number, newPassword: string) {
  try {
    const headers = await getAuthHeaders()
    const response = await apiClient.post(`/admin/change_password/${userId}`, { new_password: newPassword }, { headers })
    return { success: true, message: response.data.message }
  } catch (error: any) {
    console.error('Error al cambiar la contraseña del usuario:', error)
    return { 
      success: false, 
      message: error.response?.data?.message || 'Error al cambiar la contraseña del usuario'
    }
  }
}

export async function resetUserPassword(userId: number) {
  try {
    const headers = await getAuthHeaders()
    const response = await apiClient.post(`/admin/reset_password/${userId}`, {}, { headers })
    return { success: true, message: response.data.message }
  } catch (error: any) {
    console.error('Error al resetear la contraseña del usuario:', error)
    return { 
      success: false, 
      message: error.response?.data?.message || 'Error al resetear la contraseña del usuario'
    }
  }
}

export async function registerUser(username: string, password: string) {
  try {
    const headers = await getAuthHeaders()
    const response = await apiClient.post('/admin/register', { username, password }, { headers })
    return { success: true, message: response.data.message }
  } catch (error: any) {
    console.error('Error al registrar nuevo usuario:', error)
    return { 
      success: false, 
      message: error.response?.data?.message || 'Error al registrar nuevo usuario'
    }
  }
}
