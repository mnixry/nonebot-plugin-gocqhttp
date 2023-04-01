<template>
  <div class="text-center">
    <q-chip>
      <q-avatar color="accent" icon="developer_board" />
      <strong>CPU:</strong>
      <pre>{{ status?.cpu_percent }}%</pre>
    </q-chip>
    <q-chip>
      <q-avatar color="blue" icon="account_tree" />
      <strong>PID:</strong>
      <code>{{ status?.pid }}</code>
    </q-chip>
    <q-chip>
      <q-avatar color="yellow" icon="memory" />
      <strong>内存:</strong>
      <code>{{ ((status?.memory_used ?? 0) / 1024 ** 2).toFixed(2) }}MB</code>
    </q-chip>
    <q-chip>
      <q-avatar color="green" icon="timer" />
      <strong>进程在线时间:</strong>
      <code>{{ formatTimeDelta(uptime) }}</code>
    </q-chip>
  </div>
</template>
<script setup lang="ts">
import type { RunningProcessDetail } from 'src/api';
import { onMounted, onUnmounted, ref } from 'vue';

const uptime = ref(0),
  props = defineProps<{ status: RunningProcessDetail }>();

let uptimeRefreshTimer: number;

function formatTimeDelta(delta: number) {
  const days = Math.floor(delta / 86400000);
  delta -= days * 86400000;
  const hours = Math.floor(delta / 3600000) % 24;
  delta -= hours * 3600000;
  const minutes = Math.floor(delta / 60000) % 60;
  delta -= minutes * 60000;
  const seconds = Math.floor(delta / 1000) % 60;

  const resultString = ''
    .concat(days ? `${days}天` : '')
    .concat(hours ? `${hours}小时` : '')
    .concat(minutes ? `${minutes}分` : '')
    .concat(seconds ? `${seconds}秒` : '');

  return resultString || '0秒';
}

onMounted(() => {
  uptimeRefreshTimer = setInterval(() => {
    uptime.value = Date.now() - (props.status?.start_time ?? 0) * 1000;
  }, 1000) as unknown as number;
});

onUnmounted(() => {
  clearInterval(uptimeRefreshTimer);
});
</script>
