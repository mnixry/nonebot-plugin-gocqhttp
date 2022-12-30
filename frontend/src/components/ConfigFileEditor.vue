<template>
  <div ref="dom" class="editor" />
</template>
<style scoped lang="scss">
@import '~@fontsource/roboto-mono/index.css';

.editor {
  font-family: 'Roboto Mono', monospace, serif;
}
</style>
<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { editor } from 'monaco-editor/esm/vs/editor/editor.api.js';

const dom = ref<HTMLElement>(),
  props = defineProps<{
    modelValue: string;
    language: string;
    theme?: string;
  }>(),
  emit = defineEmits(['update:modelValue']);

let instance: editor.IStandaloneCodeEditor;

onMounted(() => {
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  instance = editor.create(dom.value!, {
    value: props.modelValue,
    language: props.language,
    theme: props.theme,
    fontFamily: 'Roboto Mono',
  });

  instance.onDidChangeModelContent(() => {
    const value = instance.getValue();
    emit('update:modelValue', value);
  });
});

watch(
  () => props.theme,
  (value) =>
    instance.updateOptions({
      theme: value,
    })
);

watch(
  () => props.modelValue,
  (value) => instance.setValue(value)
);
</script>
