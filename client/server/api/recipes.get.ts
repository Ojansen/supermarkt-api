import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

export default defineEventHandler(async () => {
  const path = resolve(process.cwd(), 'data', 'recepten.json')
  const raw = await readFile(path, 'utf-8')
  return JSON.parse(raw)
})
