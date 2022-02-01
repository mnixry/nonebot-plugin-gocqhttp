<template>
  <div class="text-center">
    <div>
      <q-circular-progress
        show-value
        :value="status?.cpu_percent"
        :track-color="$q.dark.isActive ? 'grey-8' : 'grey-3'"
        :thickness="0.1"
        size="90px"
        color="blue"
        class="q-ma-sm"
      >
        <q-icon name="developer_board" color="accent" size="30px" />
      </q-circular-progress>
      <div class="text-body1">CPU</div>
      <code class="text-body2">{{ status?.cpu_percent }}%</code>
    </div>
    <q-chip>
      <q-avatar color="blue" icon="account_tree" />
      <strong>PID:</strong><code>{{ status?.pid }}</code>
    </q-chip>
    <q-chip>
      <q-avatar color="yellow" icon="memory" />
      <strong>内存:</strong
      ><code>{{ ((status?.memory_used ?? 0) / 1024 ** 2).toFixed(2) }}MB</code>
    </q-chip>
    <q-chip>
      <q-avatar color="green" icon="timer" />
      <strong>启动时间:</strong
      ><code>{{
        new Date((status?.start_time ?? 0) * 1000).toLocaleString()
      }}</code>
    </q-chip>
  </div>
</template>
<script setup lang="ts">
import { RunningProcessDetail } from 'src/api';
import { PropType } from 'vue';

defineProps({
  status: { type: Object as PropType<RunningProcessDetail>, required: true },
});
</script>
