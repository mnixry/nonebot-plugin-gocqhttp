<template>
  <div ref="dom" />
</template>
<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { editor } from 'monaco-editor';

const props = defineProps<{
    modelValue: string;
    language: string;
    theme?: string;
  }>(),
  emit = defineEmits(['update:modelValue']),
  dom = ref<HTMLElement>();

let instance: editor.IStandaloneCodeEditor;

onMounted(() => {
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  instance = editor.create(dom.value!, {
    value: props.modelValue,
    language: props.language,
    theme: props.theme,
  });

  instance.onDidChangeModelContent(() => {
    const value = instance.getValue();
    emit('update:modelValue', value);
  });
});

watch(
  () => props.theme,
  (value) => {
    instance.updateOptions({
      theme: value,
    });
  }
);
</script>
