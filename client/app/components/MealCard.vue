<script setup lang="ts">
interface Deal {
  naam: string
  winkel: string
  aanbieding: string
  prijs_eerst: number
  prijs_nu: number
}

interface MatchedIngredient {
  naam: string
  hoeveelheid: string
  matched: boolean
  deals: Deal[]
}

interface Recipe {
  naam: string
  porties: number
  ingredienten: { naam: string, hoeveelheid: string }[]
  tags: string[]
}

const props = defineProps<{
  recept: Recipe
  score: number
  ingredienten: MatchedIngredient[]
}>()

const isRealDeal = (d: Deal) => d.prijs_nu > 0 && d.aanbieding !== 'Geen aanbieding'

const filteredIngredienten = computed(() =>
  props.ingredienten.map(ing => {
    const realDeals = ing.deals.filter(isRealDeal)
    return { ...ing, deals: realDeals, matched: realDeals.length > 0 }
  })
)

const priceSummary = computed(() => {
  let totalOriginal = 0
  let totalDiscount = 0

  for (const ing of filteredIngredienten.value) {
    if (!ing.matched) continue
    const cheapest = ing.deals.reduce((min, d) => d.prijs_nu < min.prijs_nu ? d : min, ing.deals[0]!)
    totalDiscount += cheapest.prijs_nu
    totalOriginal += cheapest.prijs_eerst > 0 ? cheapest.prijs_eerst : cheapest.prijs_nu
  }

  return {
    original: totalOriginal,
    discount: totalDiscount,
    saved: totalOriginal - totalDiscount
  }
})

const fmt = (n: number) => `€${n.toFixed(2)}`

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
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold">{{ recept.naam }}</h3>
        <UBadge color="neutral" variant="subtle">
          {{ recept.porties }} porties
        </UBadge>
      </div>
      <div v-if="priceSummary.discount > 0" class="mt-2 text-sm space-y-0.5">
        <div class="flex justify-between">
          <span class="text-muted">Normale prijs</span>
          <span class="line-through text-muted">{{ fmt(priceSummary.original) }}</span>
        </div>
        <div class="flex justify-between">
          <span>Aanbiedingsprijs</span>
          <span class="font-semibold">{{ fmt(priceSummary.discount) }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-green-600 dark:text-green-400">Bespaard</span>
          <span class="font-semibold text-green-600 dark:text-green-400">{{ fmt(priceSummary.saved) }}</span>
        </div>
      </div>
      <p class="text-xs text-muted mt-1">
        {{ filteredIngredienten.filter(i => i.matched).length }} / {{ filteredIngredienten.length }} ingredienten in de aanbieding
      </p>
    </template>

    <ul class="space-y-2">
      <li v-for="ing in filteredIngredienten" :key="ing.naam">
        <MatchBadge :matched="ing.matched" :naam="ing.naam" />
        <div v-if="ing.matched && ing.deals.length" class="ml-5.5 mt-0.5 flex flex-wrap gap-1">
          <UBadge
            v-for="deal in ing.deals.slice(0, 3)"
            :key="deal.naam + deal.winkel"
            :color="(storeColors[deal.winkel] as any)"
            variant="subtle"
            size="xs"
          >
            {{ storeLabels[deal.winkel] }}: {{ deal.aanbieding }}
          </UBadge>
        </div>
      </li>
    </ul>

    <template #footer>
      <div class="flex flex-wrap gap-1">
        <UBadge v-for="tag in recept.tags" :key="tag" color="neutral" variant="outline" size="xs">
          {{ tag }}
        </UBadge>
      </div>
    </template>
  </UCard>
</template>
