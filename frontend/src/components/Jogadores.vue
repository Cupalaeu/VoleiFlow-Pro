<script setup>
import { ref, computed, nextTick } from 'vue'
import { useVoleiStore } from '../stores/voleiStore'
import api from '../api'
import VMasker from 'vanilla-masker'

const store = useVoleiStore()

// Variáveis locais da tela
const modalAberto = ref(false)
const modoEdicao = ref(false)
const salvando = ref(false)
const inputZap = ref(null) // Referência para a máscara
const inputNome = ref(null)

const form = ref({ id: null, nome: '', sexo: 'M', whatsapp: '', avatar: '' })

const listaEmojis = ["🐶","🐱","🐭","🐹","🐰","🦊","🐻","🐼","🐻‍❄️","🐨","🐯","🦁","🐮","🐷","🐸","🐵","🐔","🐧","🐦","🐥","🦆","🐦‍⬛","🦅","🦉","🦇","🐺","🐗","🐴","🦄","🫎","🐝","🐛","🦋","🐌","🐞","🐜","🕷️","🦂","🐢","🐍","🦎","🦖","🦕","🦑","🪼","🦞","🦀","🐡","🐠","🐬","🐳","🐋","🦈","🦭","🐊","🐅","🐆","🦓","🦍","🦧","🦣","🐘","🦛","🦏","🐫","🦒","🦘","🦬","🐂","🐄","🫏","🐎","🐏","🐑","🦙","🐐","🦌","🦃","🦤","🦚","🦜","🦢","🦩","🕊️","🐇","🦝","🦨","🦡","🦫","🦦","🦥","🦔","🐉","🐲","🐦‍🔥"]

// Computados
const totalPresentes = computed(() => store.jogadores.filter(j => j.status === 'Presente').length)

// Funções do Modal
const abrirModal = (j) => {
  modalAberto.value = true
  modoEdicao.value = !!j
  if (j) {
    form.value = { ...j }
  } else {
    form.value = { id: null, nome: '', sexo: 'M', whatsapp: '', avatar: '' }
  }
  
  // Espera a tela desenhar para aplicar a máscara e dar foco
  nextTick(() => {
    if (inputZap.value) VMasker(inputZap.value).maskPattern('(99) 99999-9999')
    if (inputNome.value) inputNome.value.focus()
  })
}

const fecharModal = () => {
  modalAberto.value = false
}

const isEmojiIndisponivel = (emoji) => {
  const dono = store.jogadores.find(j => j.avatar === emoji)
  if (!dono) return false
  if (modoEdicao.value && dono.id === form.value.id) return false
  return true
}

// Funções de Banco de Dados (API Python)
const salvarJogador = async () => {
  if (!form.value.nome) return alert("Por favor, preencha o nome!")
  salvando.value = true
  
  try {
    if (modoEdicao.value) {
      await api.put(`/jogadores/${form.value.id}`, form.value)
    } else {
      await api.post('/jogadores', form.value)
    }
    await store.carregarJogadores() // Pede pro Cofre atualizar a lista
    fecharModal()
  } catch (error) {
    alert("Erro ao salvar: " + error.message)
  } finally {
    salvando.value = false
  }
}

const togglePresenca = async (j) => {
  const novoStatus = j.status === 'Presente' ? 'Ativo' : 'Presente'
  const statusAntigo = j.status
  j.status = novoStatus // Atualiza visualmente instantâneo (Otimismo UI)
  
  try {
    // Altere a rota de acordo com o que configuramos no backend Python (usando o padrão REST)
    await api.patch(`/jogadores/${j.id}/status`, { is_ativo: novoStatus === 'Presente' }) 
    // Se o backend usar o nome "status" em vez de "is_ativo", mudaremos isso
  } catch (error) {
    j.status = statusAntigo // Reverte se der erro
    alert("Erro ao alterar presença")
  }
}

const desmarcarTodos = async () => {
  if (!confirm("Deseja remover a presença de TODOS os jogadores?")) return
  
  try {
    // Para simplificar, desmarca um por um rápido, ou criaremos uma rota no Python pra isso depois
    for (const j of store.jogadores) {
      if (j.status === 'Presente') {
         j.status = 'Ativo'
         await api.patch(`/jogadores/${j.id}/status`, { is_ativo: false })
      }
    }
    store.filaIds = [] // Limpa a fila
  } catch (error) {
    alert("Erro ao desmarcar todos")
  }
}
</script>

<template>
  <div class="animate-fade-in pb-20 md:pb-0">
    <div class="flex justify-between items-center mb-4 bg-gray-900 p-2 rounded-lg border border-gray-800">
      <div class="text-xs text-gray-400 ml-2">
        <span class="text-green-400 font-bold text-sm">{{ totalPresentes }}</span> presentes
      </div>
      <div class="flex gap-2">
        <button @click="desmarcarTodos" class="bg-gray-800 hover:bg-red-900 text-gray-300 hover:text-white text-[10px] font-bold px-3 py-2 rounded flex items-center gap-1 transition border border-gray-700 hover:border-red-500">
          <span class="material-icons text-sm">person_off</span>
          <span class="hidden sm:inline">Desmarcar Todos</span>
          <span class="sm:hidden">Limpar</span>
        </button>
        <button @click="abrirModal(null)" class="bg-green-600 hover:bg-green-500 text-black text-sm font-bold px-3 py-2 rounded flex items-center gap-1 transition">
          <span class="material-icons text-sm">person_add</span> Novo
        </button>
      </div>
    </div>

    <div class="card rounded-lg shadow-lg overflow-hidden">
      <ul class="divide-y divide-gray-800">
        <li v-for="j in store.jogadores" :key="j.id" class="flex justify-between items-center p-3 hover:bg-gray-800/40 transition">
          <div class="flex items-center gap-3 flex-grow cursor-pointer" @click="abrirModal(j)"> 
            <div class="w-10 h-10 rounded-full flex items-center justify-center text-xl shadow-md bg-gray-800 border border-gray-700 shrink-0">
              {{ j.avatar || (j.sexo === 'F' ? '👩' : '👨') }}
            </div>
            <div class="min-w-0">
              <div class="font-bold text-sm truncate" :class="j.status === 'Presente' ? 'text-white' : 'text-gray-400'">{{ j.nome }}</div>
              <div class="text-[10px] text-gray-500">{{ j.whatsapp }}</div>
            </div>
          </div>
          <div class="flex flex-col items-end gap-1 ml-2">
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" class="sr-only peer" :checked="j.status === 'Presente'" @change="togglePresenca(j)">
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            </label>
          </div>
        </li>
      </ul>
      <div v-if="store.jogadores.length === 0" class="text-center p-6 text-gray-500">
        Nenhum jogador cadastrado. Clique em "Novo".
      </div>
    </div>

    <div v-if="modalAberto" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[60] p-4 animate-fade-in">
      <div class="bg-[#1e1e1e] border border-gray-600 rounded-xl shadow-2xl w-full max-w-md p-6 relative max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <span class="material-icons text-green-500">{{ modoEdicao ? 'edit' : 'person_add' }}</span> 
          {{ modoEdicao ? 'Editar' : 'Novo' }}
        </h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-gray-400 text-sm mb-1">Nome</label>
            <input v-model="form.nome" type="text" class="input-cyber" ref="inputNome">
          </div>
          <div>
            <label class="block text-gray-400 text-sm mb-1">WhatsApp</label>
            <input v-model="form.whatsapp" type="tel" class="input-cyber" ref="inputZap">
          </div>
          <div>
            <label class="block text-gray-400 text-sm mb-1">Ícone</label>
            <div class="flex flex-wrap gap-2 justify-center bg-gray-800 p-2 rounded border border-gray-700 max-h-32 overflow-y-auto">
              <button v-for="emoji in listaEmojis" :key="emoji" 
                      @click="!isEmojiIndisponivel(emoji) && (form.avatar = emoji)"
                      :disabled="isEmojiIndisponivel(emoji)"
                      class="w-8 h-8 rounded flex items-center justify-center text-xl transition border"
                      :class="[
                         form.avatar === emoji ? 'bg-green-600 border-green-500 text-white' : 'border-transparent',
                         isEmojiIndisponivel(emoji) ? 'opacity-20 cursor-not-allowed grayscale' : 'hover:bg-gray-600 cursor-pointer'
                      ]">
                {{ emoji }}
              </button>
            </div>
          </div>
          <div>
            <label class="block text-gray-400 text-sm mb-1">Sexo</label>
            <div class="grid grid-cols-2 gap-4">
              <button @click="form.sexo = 'M'" class="p-3 rounded border transition" :class="form.sexo === 'M' ? 'bg-blue-900 border-blue-500' : 'bg-gray-800 border-gray-700'"><span class="material-icons">male</span></button>
              <button @click="form.sexo = 'F'" class="p-3 rounded border transition" :class="form.sexo === 'F' ? 'bg-pink-900 border-pink-500' : 'bg-gray-800 border-gray-700'"><span class="material-icons">female</span></button>
            </div>
          </div>
        </div>
        
        <div class="flex gap-3 mt-8 pt-4 border-t border-gray-700">
          <button @click="fecharModal" class="flex-1 py-3 rounded bg-gray-700 text-white hover:bg-gray-600 transition">Cancelar</button>
          <button @click="salvarJogador" :disabled="salvando" class="flex-1 py-3 rounded bg-green-600 text-black font-bold hover:bg-green-500 transition">
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>