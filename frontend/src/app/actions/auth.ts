/* eslint-disable @typescript-eslint/no-explicit-any */
'use server'

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
    });

    const data = await response.json();
    console.log("Response login", data);

    if (data.success) {
      // Solo acceder a localStorage si estamos en el navegador
      if (typeof window !== "undefined") {
        localStorage.setItem('token', data.access_token);
      }

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
  
  const token = localStorage.getItem('access_token');  // Obtener el token de localStorage

  if (!token) {
    throw new Error('No token found, please login again');
  }

  try {
    const response = await fetch('http://localhost:5000/auth/user-info', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,  // Enviar el token en la cabecera
        'Content-Type': 'application/json',
      },
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
    // Eliminar el token del almacenamiento local
    localStorage.removeItem('access_token');

    // Opcionalmente, también puedes hacer una solicitud de logout al backend para invalidar el token
    await fetch('http://localhost:5000/auth/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    });

  } catch (error) {
    console.error('Error durante el cierre de sesión:', error);
  }
}

