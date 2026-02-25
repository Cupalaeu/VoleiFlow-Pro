<script setup>
import { onMounted } from 'vue'
import { useVoleiStore } from './stores/voleiStore'

// Injetamos o nosso cofre central no componente
const store = useVoleiStore()

// Assim que a tela carregar, mandamos o Pinia buscar os dados no Python
onMounted(() => {
  store.init()
})
</script>

<template>
  <div class="h-[100dvh] w-screen flex flex-col items-center justify-center bg-[#121212] text-gray-300 font-sans overflow-hidden gap-6">
    
    <h1 class="text-green-500 text-3xl font-black tracking-widest flex items-center gap-2">
      <span class="material-icons text-4xl">power</span>
      TESTE DE CONEXÃO
    </h1>

    <div class="card p-8 rounded-xl text-center border border-gray-700 bg-[#1e1e1e] shadow-2xl min-w-[300px]">
      <p class="text-xl mb-4 uppercase font-bold tracking-wider">Status: 
        <span :class="store.statusSistema === 'Online' ? 'text-green-400' : (store.statusSistema === 'Erro' ? 'text-red-500' : 'text-yellow-400 animate-pulse')">
          {{ store.statusSistema }}
        </span>
      </p>
      
      <div v-if="store.loading" class="animate-pulse text-gray-500 flex flex-col items-center">
        <span class="material-icons animate-spin text-3xl mb-2">autorenew</span>
        <p>Buscando dados no Python...</p>
      </div>
      
      <div v-else class="text-left mt-6 space-y-3 text-sm text-gray-400 bg-black/30 p-4 rounded-lg border border-gray-800">
        <p class="flex justify-between"><span>🏐 Jogadores Cadastrados:</span> <span class="text-white font-bold">{{ store.jogadores.length }}</span></p>
        <p class="flex justify-between"><span>👥 Pessoas na Fila:</span> <span class="text-white font-bold">{{ store.filaIds.length }}</span></p>
        <p class="flex justify-between"><span>⚙️ Tamanho do Time:</span> <span class="text-white font-bold">{{ store.config.TamanhoTime || 'N/A' }}</span></p>
      </div>
    </div>

  </div>
</template>