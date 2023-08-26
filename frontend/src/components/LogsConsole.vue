<template>
  <q-card>
    <q-card-section class="row q-gutter-x-md items-center justify-start">
      <div class="text-h5 self-start">进程日志</div>
      <q-space />
      <q-chip
        v-if="typeof connected === 'boolean'"
        @click="(event) => reconnect('reconnect', event)"
        :clickable="!connected"
        :color="connected ? 'positive' : 'negative'"
        :icon="connected ? 'link' : 'link_off'"
      >
        状态: {{ connected ? '实时' : '断开' }}
      </q-chip>
      <q-btn
        @click="scroll?.setScrollPercentage('vertical', 1, 300)"
        flat
        rounded
        icon="move_down"
        label="跳转底部"
      />
      <slot name="top-trailing" />
    </q-card-section>
    <slot name="top" />
    <q-scroll-area
      ref="scroll"
      class="page-logs"
      :style="{ height: height ?? 'calc(100vh - 10rem)' }"
    >
      <!--Terminal component, thanks to @koishijs/plugin-logger and its creator @Shigma-->
      <div ref="root" class="logs ansi-up-theme">
        <div class="line" :key="index" v-for="(line, index) in logs">
          <div v-if="typeof line === 'string'">
            <code v-html="converter.ansi_to_html(line)" />
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
import { QScrollArea } from 'quasar';
import { AnsiUp } from 'ansi_up';

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
converter.use_classes = true;

const reconnect = defineEmits(['reconnect']);

const props = defineProps<{
    logs: ProcessLog[] | string[];
    connected?: boolean;
    height?: string;
  }>(),
  root = ref<HTMLElement>(),
  scroll = ref<QScrollArea>();

watch(
  () => props.logs.length,
  async () => {
    if (!scroll.value) return;

    const wrapper = scroll.value.getScrollTarget();
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
<style lang="scss">
.ansi-up-theme {
  .ansi-black-fg {
    color: #3e424d;
  }
  .ansi-black-bg {
    background-color: #3e424d;
  }
  .ansi-black-intense-fg {
    color: #282c36;
  }
  .ansi-black-intense-bg {
    background-color: #282c36;
  }
  .ansi-red-fg {
    color: #e75c58;
  }
  .ansi-red-bg {
    background-color: #e75c58;
  }
  .ansi-red-intense-fg {
    color: #b22b31;
  }
  .ansi-red-intense-bg {
    background-color: #b22b31;
  }
  .ansi-green-fg {
    color: #00a250;
  }
  .ansi-green-bg {
    background-color: #00a250;
  }
  .ansi-green-intense-fg {
    color: #007427;
  }
  .ansi-green-intense-bg {
    background-color: #007427;
  }
  .ansi-yellow-fg {
    color: #ddb62b;
  }
  .ansi-yellow-bg {
    background-color: #ddb62b;
  }
  .ansi-yellow-intense-fg {
    color: #b27d12;
  }
  .ansi-yellow-intense-bg {
    background-color: #b27d12;
  }
  .ansi-blue-fg {
    color: #208ffb;
  }
  .ansi-blue-bg {
    background-color: #208ffb;
  }
  .ansi-blue-intense-fg {
    color: #0065ca;
  }
  .ansi-blue-intense-bg {
    background-color: #0065ca;
  }
  .ansi-magenta-fg {
    color: #d160c4;
  }
  .ansi-magenta-bg {
    background-color: #d160c4;
  }
  .ansi-magenta-intense-fg {
    color: #a03196;
  }
  .ansi-magenta-intense-bg {
    background-color: #a03196;
  }
  .ansi-cyan-fg {
    color: #60c6c8;
  }
  .ansi-cyan-bg {
    background-color: #60c6c8;
  }
  .ansi-cyan-intense-fg {
    color: #258f8f;
  }
  .ansi-cyan-intense-bg {
    background-color: #258f8f;
  }
  .ansi-white-fg {
    color: #c5c1b4;
  }
  .ansi-white-bg {
    background-color: #c5c1b4;
  }
  .ansi-white-intense-fg {
    color: #a1a6b2;
  }
  .ansi-white-intense-bg {
    background-color: #a1a6b2;
  }

  .ansi-default-inverse-fg {
    color: #ffffff;
  }
  .ansi-default-inverse-bg {
    background-color: #000000;
  }

  .ansi-bold {
    font-weight: bold;
  }
  .ansi-underline {
    text-decoration: underline;
  }
}
</style>
