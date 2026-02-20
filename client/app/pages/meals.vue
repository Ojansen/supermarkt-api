<script setup lang="ts">
const { data: dealsData, status: dealsStatus } = useFetch('/api/deals')
const { data: recipesData, status: recipesStatus } = useFetch('/api/recipes')

const deals = computed(() => (dealsData.value as any)?.deals ?? [])
const recipes = computed(() => (recipesData.value as any)?.recepten ?? [])

const { suggestions } = useMatcher(deals, recipes)

const loading = computed(() => dealsStatus.value === 'pending' || recipesStatus.value === 'pending')
</script>

<template>
  <UContainer class="py-8">
    <div class="mb-6">
      <h1 class="text-2xl font-bold">Maaltijdsuggesties</h1>
      <p class="text-muted mt-1">
        Recepten gerangschikt op ingredienten in de aanbieding
      </p>
    </div>

    <div v-if="loading" class="text-center py-12 text-muted">
      Laden...
    </div>
    <div v-else-if="suggestions.length === 0" class="text-center py-12 text-muted">
      Geen recepten met ingredienten in de aanbieding gevonden.
    </div>
    <div v-else class="grid gap-6 md:grid-cols-2">
      <MealCard
        v-for="s in suggestions"
        :key="s.recept.naam"
        :recept="s.recept"
        :score="s.score"
        :ingredienten="s.ingredienten"
      />
    </div>
  </UContainer>
</template>
