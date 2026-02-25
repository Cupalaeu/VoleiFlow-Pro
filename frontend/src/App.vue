<script setup>
import { onMounted } from 'vue'
import { useVoleiStore } from './stores/voleiStore'
import Sidebar from './components/Sidebar.vue'
import Jogadores from './components/Jogadores.vue'

const store = useVoleiStore()

onMounted(() => {
  store.init() // Liga o motor do Python quando a tela abre
})
</script>

<template>
  <div class="h-[100dvh] w-screen flex bg-[#121212] text-gray-300 font-sans overflow-hidden">
    
    <div v-if="store.mobileMenuOpen" class="fixed inset-0 bg-black/80 z-30 md:hidden backdrop-blur-sm" @click="store.mobileMenuOpen = false"></div>

    <Sidebar />

    <div class="flex-1 flex flex-col h-full relative w-full overflow-hidden">
      
      <header v-if="!store.menuExpandido" class="md:hidden flex justify-between items-center p-4 border-b border-gray-800 bg-[#121212] z-10 sticky top-0">
         <div class="flex items-center gap-3">
           <button @click="store.mobileMenuOpen = true" class="text-gray-400 hover:text-white">
             <span class="material-icons">menu</span>
           </button>
           <div class="flex items-center gap-2">
              <span class="material-icons text-green-500">sports_volleyball</span>
              <h1 class="text-lg font-bold tracking-wider">VÔLEI<span class="text-green-500">FLOW</span></h1>
           </div>
         </div>
         <div class="flex items-center gap-2">
            <span :class="store.statusClass" class="w-2 h-2 rounded-full"></span>
         </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 scroll-smooth relative overscroll-contain">
        
        <div v-if="store.loading" class="flex flex-col items-center justify-center h-full text-gray-500">
          <span class="material-icons animate-spin text-4xl mb-2">autorenew</span>
          <p>Carregando dados do servidor...</p>
        </div>

        <div v-else class="max-w-5xl mx-auto w-full h-full"> 
       <Jogadores v-if="store.viewAtual === 'jogadores'" />

       <div v-else class="flex flex-col items-center justify-center h-full text-center">
         <span class="material-icons text-6xl text-gray-700 mb-4">construction</span>
         <h2 class="text-2xl text-gray-500 font-bold uppercase tracking-widest">Em Construção: <span class="text-white">{{ store.viewAtual }}</span></h2>
       </div>
     </div>

      </main>
    </div>

  </div>
</template>