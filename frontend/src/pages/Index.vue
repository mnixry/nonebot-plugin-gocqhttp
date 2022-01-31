<template>
  <q-page class="row items-center justify-evenly q-pa-md">
    <q-card class="shadow window-width q-pa-sm">
      <div class="text-h5 q-pa-md">系统状态</div>
      <q-card-section class="row justify-evenly">
        <div class="col-12 col-sm-8 row justify-evenly">
          <div class="text-center col-6">
            <q-circular-progress
              :value="status?.cpu_percent"
              :track-color="$q.dark.isActive ? 'grey-8' : 'grey-3'"
              :thickness="0.2"
              size="16vh"
              show-value
              color="green"
              class="q-ma-sm"
            >
              <q-circular-progress
                :value="status?.process.cpu_percent"
                :track-color="$q.dark.isActive ? 'grey-9' : 'grey-4'"
                show-value
                size="15vh"
                color="purple"
              >
                <q-icon name="developer_board" size="md" color="teal" />
              </q-circular-progress>
            </q-circular-progress>
            <div class="text-body1 q-mr-sm">CPU</div>
            <div class="text-body2">总计 {{ status?.cpu_percent }}%</div>
            <div class="text-body2">
              主进程 {{ status?.process.cpu_percent }}%
            </div>
          </div>
          <div class="text-center col-6">
            <q-circular-progress
              :value="status?.memory.percent"
              :track-color="$q.dark.isActive ? 'grey-8' : 'grey-3'"
              size="15vh"
              show-value
              color="blue"
              class="q-ma-sm"
              ><q-circular-progress
                :value="
                  ((status?.process.memory_used ?? 0) /
                    (status?.memory.total ?? 0)) *
                  100
                "
                :track-color="$q.dark.isActive ? 'grey-9' : 'grey-4'"
                show-value
                size="14vh"
                color="purple"
              >
                <q-icon name="memory" size="md" color="light-green" />
              </q-circular-progress>
            </q-circular-progress>
            <div class="text-body1">内存</div>
            <div class="text-body2">{{ status?.memory.percent }}%</div>
            <div class="text-body2">
              {{
                formatBytes(status?.memory.available ?? 0) +
                '/' +
                formatBytes(status?.memory.total ?? 0)
              }}
            </div>
            <div class="text-body2">
              主进程 {{ formatBytes(status?.process.memory_used ?? 0) }}
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-4">
          <div class="text-body1">硬盘占用</div>
          <q-linear-progress
            :value="(status?.disk.percent ?? 0) / 100"
            stripe
            rounded
            size="20px"
            color="orange"
            class="q-mt-sm"
          >
            <div class="absolute-full flex flex-center">
              <q-badge>{{ status?.disk.percent }}%</q-badge>
            </div>
          </q-linear-progress>
          <div class="text-body2 text-grey q-pt-sm">
            {{ formatBytes(status?.disk.free ?? 0) }}/
            {{ formatBytes(status?.disk.total ?? 0) }}
          </div>
          <q-separator spaced />
          <div class="text-body1 q-pb-sm">开机时间</div>
          <div class="text-body2">
            {{ new Date((status?.boot_time ?? 0) * 1000).toLocaleString() }}
          </div>
          <q-separator spaced />
          <div class="text-body1 q-pb-sm">主进程启动时间</div>
          <div class="text-body2">
            {{
              new Date(
                (status?.process.start_time ?? 0) * 1000
              ).toLocaleString()
            }}
          </div>
        </div>
      </q-card-section>
      <q-card-section class="q-pa-md">
        <q-list bordered class="rounded-borders shadow">
          <q-expansion-item
            icon="insights"
            expand-separator
            label="资源使用量统计图"
          >
            <vue-apex-charts
              class="col-12 q-pa-md"
              type="area"
              ref="chart"
              height="400"
              :options="chartOptions"
              :series="chartSeries"
            /> </q-expansion-item
        ></q-list>
      </q-card-section>
      <q-separator spaced />
      <q-card-section class="row justify-end items-center">
        <q-chip icon="refresh">数据更新间隔</q-chip>
        <q-slider
          class="col-8 col-sm-4"
          v-model="updateInterval"
          snap
          :min="500"
          :max="10 * 1000"
          :step="100"
        />
        <q-badge>{{ updateInterval }}ms</q-badge>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { api } from 'src/boot/axios';
import type { SystemStatus } from 'src/api';
import { ref } from '@vue/reactivity';
import { useQuasar } from 'quasar';
import { onBeforeUnmount, watch } from 'vue';
import VueApexCharts from 'vue3-apexcharts';
import type { VueApexChartsComponent } from 'vue3-apexcharts';

const $q = useQuasar();

const status = ref<SystemStatus>();
const updateInterval = ref<number>(3000);

const LEGEND_NAMES = {
    cpuUsed: '总计CPU占用',
    cpuProcess: '主进程CPU占用',
    memoryUsed: '总计内存占用',
    memoryProcess: '主进程内存占用',
  } as const,
  chartOptions = {
    dataLabels: {
      enabled: false,
    },
    xaxis: {
      type: 'datetime',
      range: 3 * 60 * 1000,
    },
    yaxis: {
      max: 100,
      min: 0,
      decimalsInFloat: 1,
    },
    stroke: {
      curve: 'smooth',
    },
  },
  chartSeries = Object.values(LEGEND_NAMES).map((name) => ({
    name,
    data: [],
  })),
  chart = ref<VueApexChartsComponent>();

function formatBytes(bytes: number, decimals = 2) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return (bytes / Math.pow(k, i)).toFixed(dm) + sizes[i];
}

let updateTimer: number;
async function updateStatus() {
  try {
    $q.loadingBar.start();
    const { data } = await api.systemStatusApiStatusGet();
    status.value = data;
    const nowDate = Date.now();

    void chart.value?.appendData(
      Object.entries({
        [LEGEND_NAMES.cpuUsed]: data.cpu_percent,
        [LEGEND_NAMES.cpuProcess]: data.process.cpu_percent,
        [LEGEND_NAMES.memoryUsed]: data.memory.percent,
        [LEGEND_NAMES.memoryProcess]:
          (data.process.memory_used / data.memory.total) * 100,
      }).map(([name, value]) => ({
        name,
        data: [
          {
            x: nowDate,
            y: value,
          },
        ],
      }))
    );
  } finally {
    $q.loadingBar.stop();
    updateTimer = window.setTimeout(
      () => void updateStatus(),
      updateInterval.value
    );
  }
}

onBeforeUnmount(() => {
  window.clearTimeout(updateTimer);
});

watch(
  () => $q.dark.isActive,
  () =>
    void chart.value?.updateOptions({
      theme: { mode: $q.dark.isActive ? 'dark' : 'light' },
    })
);

void updateStatus();
</script>
