import { normalize } from './useDeals'

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

function matchIngredient(ingredientName: string, deals: Deal[]): Deal[] {
  const norm = normalize(ingredientName)
  const tokens = norm.split(/\s+/).filter(t => t.length >= 3)
  const matched: Deal[] = []

  for (const deal of deals) {
    const dealNorm = normalize(deal.naam)
    const itemNorms = deal.items.map(i => normalize(i))

    // Tier 1: exact substring
    if (dealNorm.includes(norm) || itemNorms.some(i => i.includes(norm))) {
      matched.push(deal)
      continue
    }

    // Tier 2: all tokens present
    if (tokens.length > 1) {
      const allInDeal = tokens.every(t => dealNorm.includes(t))
      const allInItems = itemNorms.some(item => tokens.every(t => item.includes(t)))
      if (allInDeal || allInItems) {
        matched.push(deal)
        continue
      }
    }

    // Tier 3: any token >=3 chars is a substring (Dutch compounds)
    if (tokens.some(t => dealNorm.includes(t) || itemNorms.some(i => i.includes(t)))) {
      matched.push(deal)
    }
  }

  return matched
}

export function useMatcher(deals: Ref<Deal[]>, recipes: Ref<Recipe[]>) {
  const suggestions = computed<MealSuggestion[]>(() => {
    if (!deals.value.length || !recipes.value.length) return []

    return recipes.value
      .map((recept) => {
        const ingredienten: MatchedIngredient[] = recept.ingredienten.map((ing) => {
          const matchedDeals = matchIngredient(ing.naam, deals.value)
          return {
            naam: ing.naam,
            hoeveelheid: ing.hoeveelheid,
            matched: matchedDeals.length > 0,
            deals: matchedDeals
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
