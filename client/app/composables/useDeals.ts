interface Deal {
  naam: string
  omschrijving: string
  items: string[]
  aanbieding: string
  prijs_eerst: number
  prijs_nu: number
  winkel: string
}

interface DealsResponse {
  week: number
  deals: Deal[]
}

export function useDeals() {
  const { data, status } = useFetch<DealsResponse>('/api/deals')

  const winkel = ref<string>('alle')
  const zoek = ref('')
  const sorteer = ref<'winkel' | 'naam' | 'prijs_nu'>('winkel')

  const debouncedZoek = ref('')
  let timeout: ReturnType<typeof setTimeout>
  watch(zoek, (val) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => { debouncedZoek.value = val }, 300)
  })

  const week = computed(() => data.value?.week ?? 0)
  const deals = computed(() => data.value?.deals ?? [])

  const filteredDeals = computed(() => {
    let result = deals.value

    if (winkel.value !== 'alle') {
      result = result.filter(d => d.winkel === winkel.value)
    }

    if (debouncedZoek.value) {
      const q = normalize(debouncedZoek.value)
      result = result.filter(d =>
        normalize(d.naam).includes(q)
        || normalize(d.aanbieding).includes(q)
        || d.items.some(i => normalize(i).includes(q))
      )
    }

    result = [...result].sort((a, b) => {
      if (sorteer.value === 'prijs_nu') return a.prijs_nu - b.prijs_nu
      if (sorteer.value === 'naam') return a.naam.localeCompare(b.naam, 'nl')
      return a.winkel.localeCompare(b.winkel) || a.naam.localeCompare(b.naam, 'nl')
    })

    return result
  })

  return { deals, filteredDeals, week, winkel, zoek, sorteer, status }
}

export function normalize(text: string): string {
  return text
    .toLowerCase()
    .replace(/^(ah|jumbo|plus|kruidvat|lidl|aldi|dirk|vomar|hoogvliet|poiesz|dekamarkt|spar|boni|nettorama|trekpleister|makro|coop|mcd|boons)\s+/i, '')
    .replace(/\d+\s*(g|gram|kg|ml|l|liter|cl|stuks?)\b/gi, '')
    .trim()
}
