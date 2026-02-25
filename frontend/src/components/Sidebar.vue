<script setup>
import { useVoleiStore } from '../stores/voleiStore'

// Conectamos a Sidebar ao Cofre Central
const store = useVoleiStore()

const toggleMenuPrincipal = () => {
  if (window.innerWidth < 768) {
    store.mobileMenuOpen = !store.mobileMenuOpen
  } else {
    store.menuExpandido = !store.menuExpandido
  }
}

const mudarView = (view) => {
  store.viewAtual = view
  store.mobileMenuOpen = false
}
</script>

<template>
  <aside class="fixed inset-y-0 left-0 z-40 bg-[#1e1e1e] border-r border-gray-800 transition-transform duration-300 transform md:static md:translate-x-0 flex flex-col"
         :class="[
           store.mobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
           store.menuExpandido ? 'md:w-48 w-64' : 'md:w-16'
         ]">
    
    <div class="h-16 flex items-center justify-center border-b border-gray-800 cursor-pointer hover:bg-gray-800 transition"
         @click="toggleMenuPrincipal">
       <span v-if="!store.menuExpandido && !store.mobileMenuOpen" class="material-icons text-green-500">menu</span>
       <span v-else-if="store.mobileMenuOpen" class="material-icons text-gray-400 md:hidden">close</span>
       
       <div v-if="store.menuExpandido || store.mobileMenuOpen" class="flex items-center gap-2 animate-fade-in px-2">
         <span class="material-icons text-green-500 hidden md:block">sports_volleyball</span>
         <h1 class="font-bold tracking-wider text-white text-lg">VÔLEI<span class="text-green-500">FLOW</span></h1>
       </div>
    </div>

    <nav class="flex-1 py-4 flex flex-col gap-2">
      
      <button @click="mudarView('jogadores')" 
              class="flex items-center px-4 py-3 hover:bg-gray-800 transition relative group" 
              :class="store.viewAtual === 'jogadores' ? 'border-r-4 border-green-500 bg-gray-800/50 text-green-400' : 'text-gray-500'">
        <span class="material-icons text-2xl">people</span>
        <span v-if="store.menuExpandido || store.mobileMenuOpen" class="ml-3 font-medium text-sm whitespace-nowrap animate-fade-in">Jogadores</span>
        <div v-if="!store.menuExpandido && !store.mobileMenuOpen" class="hidden md:block absolute left-14 bg-gray-900 text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition pointer-events-none z-50 border border-gray-700">Jogadores</div>
      </button>

      <button @click="mudarView('quadra')" 
              class="flex items-center px-4 py-3 hover:bg-gray-800 transition relative group" 
              :class="store.viewAtual === 'quadra' ? 'border-r-4 border-green-500 bg-gray-800/50 text-green-400' : 'text-gray-500'">
        <div class="relative">
          <span class="material-icons text-2xl">sports_volleyball</span>
          <span v-if="store.algumaQuadraAtiva" class="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full animate-pulse border border-[#1e1e1e]"></span>
        </div>
        <span v-if="store.menuExpandido || store.mobileMenuOpen" class="ml-3 font-medium text-sm whitespace-nowrap animate-fade-in">Quadras</span>
        <div v-if="!store.menuExpandido && !store.mobileMenuOpen" class="hidden md:block absolute left-14 bg-gray-900 text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition pointer-events-none z-50 border border-gray-700">Quadras</div>
      </button>

      <button @click="mudarView('config')" 
              class="flex items-center px-4 py-3 hover:bg-gray-800 transition relative group" 
              :class="store.viewAtual === 'config' ? 'border-r-4 border-blue-500 bg-gray-800/50 text-blue-400' : 'text-gray-500'">
        <span class="material-icons text-2xl">settings</span>
        <span v-if="store.menuExpandido || store.mobileMenuOpen" class="ml-3 font-medium text-sm whitespace-nowrap animate-fade-in">Regras</span>
        <div v-if="!store.menuExpandido && !store.mobileMenuOpen" class="hidden md:block absolute left-14 bg-gray-900 text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition pointer-events-none z-50 border border-gray-700">Regras</div>
      </button>

    </nav>

    <div class="p-4 border-t border-gray-800 text-center">
       <div class="flex justify-center items-center gap-2" :title="store.statusSistema">
         <span :class="store.statusClass" class="w-2 h-2 rounded-full"></span>
         <span v-if="store.menuExpandido || store.mobileMenuOpen" class="text-[10px] uppercase tracking-widest text-gray-500">{{ store.statusSistema }}</span>
       </div>
    </div>

  </aside>
</template>