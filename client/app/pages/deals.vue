<script setup lang="ts">
const { filteredDeals, week, winkel, zoek, sorteer, status } = useDeals()
</script>

<template>
  <UContainer class="py-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">
        Aanbiedingen
        <span v-if="week" class="text-muted font-normal text-lg">week {{ week }}</span>
      </h1>
    </div>

    <div class="flex flex-col sm:flex-row gap-4 mb-6">
      <StoreFilter v-model="winkel" />
      <UInput
        v-model="zoek"
        placeholder="Zoek product..."
        icon="i-lucide-search"
        class="sm:max-w-xs"
      />
      <USelect
        v-model="sorteer"
        :items="[
          { label: 'Winkel', value: 'winkel' },
          { label: 'Naam', value: 'naam' },
          { label: 'Prijs', value: 'prijs_nu' }
        ]"
        class="sm:max-w-32"
      />
    </div>

    <div v-if="status === 'pending'" class="text-center py-12 text-muted">
      Laden...
    </div>
    <div v-else-if="filteredDeals.length === 0" class="text-center py-12 text-muted">
      Geen aanbiedingen gevonden.
    </div>
    <DealTable v-else :deals="filteredDeals" />
  </UContainer>
</template>
