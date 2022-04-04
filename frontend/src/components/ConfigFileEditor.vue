<template>
  <div ref="dom" />
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { editor } from 'monaco-editor';

interface Props
  extends Omit<editor.IStandaloneEditorConstructionOptions, 'value'> {
  modelValue: string;
}

const props = defineProps<Props>(),
  emit = defineEmits(['update:modelValue']),
  dom = ref<HTMLElement>();

let instance: editor.IStandaloneCodeEditor;

onMounted(() => {
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  instance = editor.create(dom.value!, {
    value: props.modelValue,
    ...props,
  });

  instance.onDidChangeModelContent(() => {
    const value = instance.getValue();
    emit('update:modelValue', value);
  });
});
</script>
