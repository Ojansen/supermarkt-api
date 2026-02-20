import Fuse from 'fuse.js'

interface Deal {
  naam: string
  omschrijving: string
  items: string[]
  aanbieding: string
  prijs_eerst: number
  prijs_nu: number
  winkel: string
}

interface Ingredient {
  naam: string
  hoeveelheid: string
}

interface Recipe {
  naam: string
  porties: number
  ingredienten: Ingredient[]
  tags: string[]
}

interface MatchedIngredient {
  naam: string
  hoeveelheid: string
  matched: boolean
  deals: Deal[]
}

interface MealSuggestion {
  recept: Recipe
  score: number
  ingredienten: MatchedIngredient[]
}

export function useMatcher(deals: Ref<Deal[]>, recipes: Ref<Recipe[]>) {
  const fuse = computed(() => new Fuse(deals.value, {
    keys: ['naam', 'items'],
    threshold: 0.4,
    ignoreLocation: true,
  }))

  const suggestions = computed<MealSuggestion[]>(() => {
    if (!deals.value.length || !recipes.value.length) return []

    return recipes.value
      .map((recept) => {
        const ingredienten: MatchedIngredient[] = recept.ingredienten.map((ing) => {
          const results = fuse.value.search(ing.naam)
          const matchedDeals = results.map(r => r.item)
          return {
            naam: ing.naam,
            hoeveelheid: ing.hoeveelheid,
            matched: matchedDeals.length > 0,
            deals: matchedDeals,
          }
        })

        const matchCount = ingredienten.filter(i => i.matched).length
        const score = matchCount / ingredienten.length

        return { recept, score, ingredienten }
      })
      .filter(s => s.score > 0)
      .sort((a, b) => b.score - a.score)
  })

  return { suggestions }
}
