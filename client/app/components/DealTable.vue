<script setup lang="ts">
interface Deal {
  naam: string
  omschrijving: string
  items: string[]
  aanbieding: string
  prijs_eerst: number
  prijs_nu: number
  winkel: string
}

defineProps<{
  deals: Deal[]
}>()

const storeColors: Record<string, string> = {
  ah: 'info',
  jumbo: 'warning',
  plus: 'success',
  kruidvat: 'error',
  lidl: 'info',
  aldi: 'info',
  dirk: 'warning',
  vomar: 'success',
  hoogvliet: 'warning',
  poiesz: 'success',
  dekamarkt: 'error',
  spar: 'success',
  boni: 'warning',
  nettorama: 'error',
  trekpleister: 'error',
  makro: 'info',
  coop: 'success',
  mcd: 'warning',
  boons: 'info',
}

const storeLabels: Record<string, string> = {
  ah: 'AH',
  jumbo: 'Jumbo',
  plus: 'Plus',
  kruidvat: 'Kruidvat',
  lidl: 'Lidl',
  aldi: 'Aldi',
  dirk: 'Dirk',
  vomar: 'Vomar',
  hoogvliet: 'Hoogvliet',
  poiesz: 'Poiesz',
  dekamarkt: 'Dekamarkt',
  spar: 'Spar',
  boni: 'Boni',
  nettorama: 'Nettorama',
  trekpleister: 'Trekpleister',
  makro: 'Makro',
  coop: 'Coop',
  mcd: 'MCD',
  boons: 'Boons',
}

const columns = [
  { accessorKey: 'winkel', header: 'Winkel' },
  { accessorKey: 'naam', header: 'Product' },
  { accessorKey: 'aanbieding', header: 'Aanbieding' },
  { accessorKey: 'prijs_nu', header: 'Prijs' }
] satisfies { accessorKey: keyof Deal, header: string }[]
</script>

<template>
  <UTable :data="deals" :columns="columns">
    <template #winkel-cell="{ row }">
      <UBadge :color="(storeColors[row.original.winkel] as any)" variant="subtle">
        {{ storeLabels[row.original.winkel] ?? row.original.winkel }}
      </UBadge>
    </template>
    <template #naam-cell="{ row }">
      <span class="font-medium">{{ row.original.naam }}</span>
    </template>
    <template #aanbieding-cell="{ row }">
      <span class="text-muted">{{ row.original.aanbieding }}</span>
    </template>
    <template #prijs_nu-cell="{ row }">
      <span v-if="row.original.prijs_nu" class="font-semibold">
        &euro;{{ row.original.prijs_nu.toFixed(2) }}
      </span>
    </template>
  </UTable>
</template>
