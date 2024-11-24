import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL, // URL de mi backend
  withCredentials: true, // Necesario para enviar cookies de sesión
});

export default apiClient;
