/* eslint-disable @typescript-eslint/no-explicit-any */
'use server'

import { cookies } from 'next/headers'

export async function login(prevState: any, formData: FormData) {
  const username = formData.get('username') as string;
  const password = formData.get('password') as string;

  try {
    const response = await fetch('http://localhost:5000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
      credentials: 'include', // Asegúrate de incluir las credenciales (cookies)
    });

    const data = await response.json();
    console.log("Response login", data);

    if (data.success) {
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
    const response = await fetch('http://localhost:5000/auth/user-info', {
      method: 'GET',
      credentials: 'include',  // Asegúrate de incluir las credenciales (cookies)
    });

    if (!response.ok) {
      throw new Error('Error al obtener la información del usuario');
    }

    const data = await response.json();
    console.log("Response GetUser", data);
    return data;
  } catch (error) {
    console.error('Error al obtener la información del usuario:', error);
    throw error;
  }
}

export async function logout() {
  try {
    await fetch('http://localhost:5000/auth/logout', {
      method: 'POST',
      credentials: 'include', // Asegúrate de incluir las credenciales (cookies)
    });

    // Eliminar la cookie en el cliente (usando `cookies()` de Next.js)
    const cookieStore = await cookies();
    cookieStore.delete('session');
  } catch (error) {
    console.error('Error durante el cierre de sesión:', error);
  }
}
