<template>
  <q-card>
    <q-card-section>
      <div class="text-h6">
        进程日志
        <q-chip
          v-if="typeof connected === 'boolean'"
          @click="(event) => reconnect('reconnect', event)"
          :clickable="!connected"
          :color="connected ? 'positive' : 'negative'"
          :icon="connected ? 'link' : 'link_off'"
        >
          状态: {{ connected ? '实时' : '断开' }}
        </q-chip>
      </div>
    </q-card-section>
    <q-scroll-area
      class="page-logs"
      :style="{ height: height ?? 'calc(100vh - 10rem)' }"
    >
      <!--Terminal component, thanks to @koishijs/plugin-logger and its creator @Shigma-->
      <div ref="root" class="logs">
        <div class="line" :key="index" v-for="(line, index) in logs">
          <div v-if="typeof line === 'string'">
            <code v-html="converter.ansi_to_html(line)"></code>
          </div>
          <div
            v-else
            :class="{ start: line.message.startsWith(START_LINE_MARK) }"
          >
            <code v-if="line.time" class="timestamp">
              {{ new Date(line.time).toLocaleString() }}
            </code>
            <code v-if="line.level" class="level">{{ line.level }}</code>
            <code
              v-html="converter.ansi_to_html(line.message)"
              :class="LOG_LEVEL_MAP[line.level ?? ProcessLogLevel.Stdout]"
            />
          </div>
        </div>
      </div>
    </q-scroll-area>
  </q-card>
</template>
<script setup lang="ts">
import { nextTick, watch, ref } from 'vue';
import AnsiUp from 'ansi_up';

import { type ProcessLog, ProcessLogLevel } from 'src/api';

const START_LINE_MARK = '当前版本:',
  LOG_LEVEL_MAP = {
    [ProcessLogLevel.Debug]: 'level-debug',
    [ProcessLogLevel.Info]: 'level-info',
    [ProcessLogLevel.Warning]: 'level-warn',
    [ProcessLogLevel.Error]: 'level-error',
    [ProcessLogLevel.Fatal]: 'level-fatal',
    [ProcessLogLevel.Stdout]: 'stdout',
  };

const converter = new AnsiUp();

const props = defineProps<{
    logs: ProcessLog[] | string[];
    connected?: boolean;
    height?: string;
  }>(),
  reconnect = defineEmits(['reconnect']),
  root = ref<HTMLElement>();

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
@import '~@fontsource/roboto-mono/index.css';

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
  color: var(--terminal-fg);
  background-color: var(--terminal-bg);
  .logs {
    padding: 1rem 1rem;
    code {
      font-family: 'Roboto Mono', monospace, serif;
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
