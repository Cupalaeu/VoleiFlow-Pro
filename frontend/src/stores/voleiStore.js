// src/stores/voleiStore.js
import { defineStore } from 'pinia';
import api from '../api';

export const useVoleiStore = defineStore('volei', {
  // 1. STATE: As variáveis globais
  state: () => ({
    statusSistema: 'Desconectado',
    loading: true,
    jogadores: [],
    filaIds: [],
    jogos: {},
    config: {},
    // -- Variáveis de Interface (Novas) --
    viewAtual: 'jogadores',
    menuExpandido: false,
    mobileMenuOpen: false,
  }),

  // 1.5 GETTERS: Variáveis calculadas automaticamente (O antigo "computed")
  getters: {
    statusClass: (state) => state.statusSistema === 'Online' ? 'bg-green-500' : (state.statusSistema === 'Erro' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'),
    algumaQuadraAtiva: (state) => (state.jogos[1] && state.jogos[1].status === 'JOGANDO') || (state.jogos[2] && state.jogos[2].status === 'JOGANDO'),
  },

  // 2. ACTIONS: As funções que alteram o state (Os antigos methods)
  actions: {
    // Função principal que arranca o sistema
    async init() {
      this.statusSistema = 'A ligar...';
      try {
        // Dispara as 3 requisições ao mesmo tempo para ser rápido (igual ao Promise.all do GAS)
        await Promise.all([
          this.carregarJogadores(),
          this.carregarEstado(),
          this.carregarConfig()
        ]);
        this.statusSistema = 'Online';
      } catch (error) {
        console.error("Erro ao comunicar com o Python:", error);
        this.statusSistema = 'Erro';
      } finally {
        this.loading = false;
      }
    },

    async carregarJogadores() {
      const response = await api.get('/jogadores');
      this.jogadores = response.data;
    },

    async carregarEstado() {
      const response = await api.get('/estado');
      this.filaIds = response.data.fila || [];
      this.jogos = response.data.jogos || {};
    },

    async carregarConfig() {
      const response = await api.get('/configuracoes');
      // O Python devolve uma lista [{chave: 'TamanhoTime', valor: 4}, ...]
      // Vamos converter num objeto simples { TamanhoTime: 4 } para ficar igual ao seu GAS
      const configObj = {};
      response.data.forEach(item => {
        configObj[item.chave] = item.valor;
      });
      this.config = configObj;
    }
  }
});