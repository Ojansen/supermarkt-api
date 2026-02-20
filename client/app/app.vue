<script setup>
useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ],
  link: [
    { rel: 'icon', href: '/favicon.ico' }
  ],
  htmlAttrs: {
    lang: 'nl'
  }
})

const title = 'Supermarkt Deals'
const description = 'Vergelijk weekaanbiedingen van Albert Heijn, Jumbo, Plus en Kruidvat. Vind maaltijdsuggesties op basis van aanbiedingen.'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description
})

const navItems = [
  { label: 'Deals', to: '/deals', icon: 'i-lucide-tag' },
  { label: 'Maaltijden', to: '/meals', icon: 'i-lucide-chef-hat' }
]
</script>

<template>
  <UApp>
    <UHeader>
      <template #left>
        <NuxtLink to="/" class="font-bold text-lg">
          Supermarkt Deals
        </NuxtLink>

        <nav class="hidden sm:flex items-center gap-1 ml-4">
          <UButton
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            :label="item.label"
            :icon="item.icon"
            variant="ghost"
            color="neutral"
          />
        </nav>
      </template>

      <template #right>
        <UColorModeButton />
      </template>
    </UHeader>

    <UMain>
      <NuxtPage />
    </UMain>

    <USeparator />

    <UFooter>
      <template #left>
        <p class="text-sm text-muted">
          Supermarkt Deals
        </p>
      </template>
    </UFooter>
  </UApp>
</template>
