// src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // O endereço do nosso FastAPI
  timeout: 5000,
});

export default api;