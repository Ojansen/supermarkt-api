<template>
  <UContainer class="py-16 text-center">
    <h1 class="text-4xl font-bold mb-4">Supermarkt Deals</h1>
    <p class="text-lg text-muted mb-8 max-w-lg mx-auto">
      Vergelijk weekaanbiedingen van Albert Heijn, Jumbo, Plus en Kruidvat.
      Ontdek maaltijdsuggesties op basis van wat in de aanbieding is.
    </p>

    <div class="flex justify-center gap-4">
      <UButton
        to="/deals"
        label="Bekijk deals"
        icon="i-lucide-tag"
        size="xl"
        trailing-icon="i-lucide-arrow-right"
      />
      <UButton
        to="/meals"
        label="Maaltijdsuggesties"
        icon="i-lucide-chef-hat"
        size="xl"
        color="neutral"
        variant="subtle"
      />
    </div>
  </UContainer>
</template>
