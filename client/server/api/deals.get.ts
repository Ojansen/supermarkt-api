import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const stores = [
  'ah', 'jumbo', 'plus', 'kruidvat', 'lidl', 'aldi', 'dirk', 'vomar',
  'hoogvliet', 'poiesz', 'dekamarkt', 'spar', 'boni', 'nettorama',
  'trekpleister', 'makro', 'coop', 'mcd', 'boons',
] as const

interface RawProduct {
  naam: string
  omschrijving: string
  items: string[]
  aanbieding: string
  prijs_eerst: number
  prijs_nu: number
}

interface StoreFile {
  week: number
  producten: RawProduct[]
}

export default defineEventHandler(async () => {
  const baseDir = resolve(process.cwd(), '..', 'public', 'v1')
  let week = 0
  const deals: (RawProduct & { winkel: string })[] = []

  for (const store of stores) {
    try {
      const raw = await readFile(resolve(baseDir, `${store}.json`), 'utf-8')
      const data: StoreFile = JSON.parse(raw)
      if (data.week) week = data.week
      for (const product of data.producten) {
        deals.push({ ...product, winkel: store })
      }
    }
    catch (e) {
      console.warn(`Failed to read ${store}.json:`, e)
    }
  }

  return { week, deals }
})
