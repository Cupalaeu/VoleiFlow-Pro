// src/api.js
import axios from 'axios';

// A mágica: pega o IP (ou localhost) de onde a página acabou de ser carregada!
const ipAtual = window.location.hostname;

const api = axios.create({
  baseURL: `http://${ipAtual}:8000`, // Usa a crase (backtick) para injetar a variável
  timeout: 5000,
});

export default api;