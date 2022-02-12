<template>
  <q-scroll-area class="page-logs">
    <!--Terminal component, thanks to @koishijs/plugin-logger and its creator @Shigma-->
    <div ref="root" class="logs rounded-borders">
      <div
        class="line"
        :class="{ start: line.message.startsWith(START_LINE_MARK) }"
        :key="line.time"
        v-for="line in logs"
      >
        <code v-if="line.time" class="timestamp">{{
          new Date(line.time).toUTCString()
        }}</code>
        <code v-if="line.level" class="level">{{ line.level }}</code>
        <code v-html="renderLine(line)" :class="lineLevel(line)"></code>
      </div>
    </div>
  </q-scroll-area>
</template>
<script setup lang="ts">
import { PropType, nextTick, watch, ref } from 'vue';
import { type ProcessLog, ProcessLogLevel } from 'src/api';
import AnsiUp from 'ansi_up';

const START_LINE_MARK = '当前版本:';
const converter = new AnsiUp();

const props = defineProps({
  logs: { type: Array as PropType<ProcessLog[]>, default: () => [] },
});
const root = ref<HTMLElement>();

function renderLine(line: ProcessLog): string {
  const text = converter.ansi_to_html(line.message);
  return text;
}

function lineLevel(line: ProcessLog) {
  switch (line.level) {
    case ProcessLogLevel.Debug:
      return 'level-debug';
    case ProcessLogLevel.Info:
      return 'level-info';
    case ProcessLogLevel.Warning:
      return 'level-warn';
    case ProcessLogLevel.Error:
      return 'level-error';
    case ProcessLogLevel.Fatal:
      return 'level-fatal';
    default:
      return 'stdout';
  }
}

watch(
  () => props.logs.length,
  async () => {
    const wrapper = root.value?.parentElement?.parentElement;
    if (!wrapper) return;
    const { scrollTop, clientHeight, scrollHeight } = wrapper;
    if (Math.abs(scrollTop + clientHeight - scrollHeight) <= 1) {
      await nextTick();
      wrapper.scrollTop = scrollHeight;
    }
  }
);
</script>
<style lang="scss">
@import '~@fontsource/source-code-pro/index.css';

:root {
  --terminal-bg: #24292f;
  --terminal-fg: #d0d7de;
  --terminal-bg-hover: #32383f;
  --terminal-fg-hover: #f6f8fa;
  --terminal-bg-selection: rgba(33, 139, 255, 0.15);
  --terminal-separator: rgba(140, 149, 159, 0.75);
  --terminal-timestamp: #8c959f;

  --terminal-debug: #4194e7;
  --terminal-info: #86e6f3;
  --terminal-warn: #f8c471;
  --terminal-error: #f37672;
  --terminal-fatal: #f72a1b;
}

.page-logs {
  height: calc(100vh - 10rem);
  color: var(--terminal-fg);
  background-color: var(--terminal-bg);
  .logs {
    padding: 1rem 1rem;
    code {
      font-family: Source Code Pro, Consolas, Menlo, Monaco, Lucida Console,
        Liberation Mono, DejaVu Sans Mono, Bitstream Vera Sans Mono, Courier New,
        monospace, serif;
    }
  }
  .logs .line.start {
    margin-top: 1rem;
    &::before {
      content: '';
      position: absolute;
      left: 0;
      right: 0;
      top: -0.5rem;
      border-top: 1px solid var(--terminal-separator);
    }
  }
  .logs:first-child .line:first-child {
    margin-top: 0;
    &::before {
      display: none;
    }
  }
  .line {
    padding: 0 0.5rem;
    border-radius: 2px;
    font-size: 14px;
    line-height: 20px;
    white-space: pre-wrap;
    position: relative;
    &:hover {
      color: var(--terminal-fg-hover);
      background-color: var(--terminal-bg-hover);
    }
    ::selection {
      background-color: var(--terminal-bg-selection);
    }
    .timestamp {
      color: var(--terminal-timestamp);
      font-size: 12px;
      font-weight: bold;
      margin-right: 0.5rem;
    }
    .level {
      color: var(--terminal-fg);
      font-weight: bold;
      margin-right: 0.5rem;
    }
    .level-debug {
      color: var(--terminal-debug);
    }
    .level-info {
      color: var(--terminal-info);
    }
    .level-warn {
      color: var(--terminal-warn);
    }
    .level-error {
      color: var(--terminal-error);
    }
    .level-fatal {
      color: var(--terminal-fatal);
    }
    .stdout {
      color: var(--terminal-fg);
    }
  }
}
</style>
