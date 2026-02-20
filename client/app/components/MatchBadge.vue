<script setup lang="ts">
defineProps<{
  matched: boolean
  naam: string
}>()
</script>

<template>
  <span class="inline-flex items-center gap-1.5">
    <UIcon
      :name="matched ? 'i-lucide-check-circle' : 'i-lucide-circle'"
      :class="matched ? 'text-green-500' : 'text-neutral-400'"
      class="size-4 shrink-0"
    />
    <span :class="matched ? 'font-medium' : 'text-muted'">
      {{ naam }}
    </span>
  </span>
</template>
