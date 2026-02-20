<script setup lang="ts">
const winkel = defineModel<string>({ default: 'alle' })

const stores = [
  { value: 'alle', label: 'Alle' },
  { value: 'ah', label: 'AH' },
  { value: 'jumbo', label: 'Jumbo' },
  { value: 'plus', label: 'Plus' },
  { value: 'kruidvat', label: 'Kruidvat' },
  { value: 'lidl', label: 'Lidl' },
  { value: 'aldi', label: 'Aldi' },
  { value: 'dirk', label: 'Dirk' },
  { value: 'vomar', label: 'Vomar' },
  { value: 'hoogvliet', label: 'Hoogvliet' },
  { value: 'poiesz', label: 'Poiesz' },
  { value: 'dekamarkt', label: 'Dekamarkt' },
  { value: 'spar', label: 'Spar' },
  { value: 'boni', label: 'Boni' },
  { value: 'nettorama', label: 'Nettorama' },
  { value: 'trekpleister', label: 'Trekpleister' },
  { value: 'makro', label: 'Makro' },
  { value: 'coop', label: 'Coop' },
  { value: 'mcd', label: 'MCD' },
  { value: 'boons', label: 'Boons' },
]
</script>

<template>
  <UButtonGroup>
    <UButton
      v-for="store in stores"
      :key="store.value"
      :label="store.label"
      :variant="winkel === store.value ? 'solid' : 'outline'"
      :color="winkel === store.value ? 'primary' : 'neutral'"
      @click="winkel = store.value"
    />
  </UButtonGroup>
</template>
