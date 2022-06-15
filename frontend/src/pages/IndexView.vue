<template>
  <q-page class="row items-stretch justify-start q-ma-md">
    <div
      class="q-pa-sm col-12 col-lg-4 col-md-6 q-gutter-y-sm items-baseline justify-evenly"
    >
      <q-card class="col-12 col-lg-6">
        <q-card-section class="card-title">
          <div class="text-h5">CPU占用</div>
        </q-card-section>
        <q-card-section horizontal>
          <q-card-section>
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
          </q-card-section>
          <q-separator vertical />
          <q-card-section>
            <div class="text-body1 q-py-sm">
              总计
              <span class="digit-display q-mx-sm">
                {{ status?.cpu_percent.toPrecision(3) }}%
              </span>
            </div>
            <q-separator spaced />
            <div class="text-body1 q-py-sm">
              主进程
              <span class="digit-display q-mx-sm">
                {{ status?.process.cpu_percent.toPrecision(3) }}%
              </span>
            </div>
          </q-card-section>
        </q-card-section>
      </q-card>
      <q-card class="col-12 col-lg-6">
        <q-card-section class="card-title">
          <div class="text-h5">内存占用</div>
        </q-card-section>
        <q-card-section horizontal>
          <q-card-section>
            <q-circular-progress
              :value="status?.memory.percent"
              :track-color="$q.dark.isActive ? 'grey-8' : 'grey-3'"
              :thickness="0.2"
              size="16vh"
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
                size="15vh"
                color="purple"
              >
                <q-icon name="memory" size="md" color="light-green" />
              </q-circular-progress>
            </q-circular-progress>
          </q-card-section>
          <q-separator vertical />
          <q-card-section>
            <div class="text-body1">
              内存
              <span class="digit-display q-mx-sm"
                >{{ status?.memory.percent }}%</span
              >
            </div>
            <q-separator spaced />
            <div class="row text-body1">
              <div class="q-mr-sm q-my-sm">
                剩余
                <span class="digit-display">
                  {{ formatBytes(status?.memory.available ?? 0) }}
                </span>
              </div>
              <div class="q-my-sm">
                总计
                <span class="digit-display">
                  {{ formatBytes(status?.memory.total ?? 0) }}
                </span>
              </div>
            </div>
            <q-separator spaced />
            <div class="text-body1 q-py-sm">
              主进程
              <span class="digit-display q-mx-sm">
                {{ formatBytes(status?.process.memory_used ?? 0) }}
              </span>
            </div>
          </q-card-section>
        </q-card-section>
      </q-card>
      <q-card class="col-12 col-md-6">
        <q-card-section class="card-title">
          <div class="text-h5">系统信息</div>
        </q-card-section>
        <q-card-section class="row justify-evenly">
          <div class="col-12">
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
      </q-card>
      <q-card class="col-12 col-md-6">
        <q-card-section class="card-title">
          <div class="text-h5">资源统计</div>
        </q-card-section>
        <q-card-section>
          <vue-apex-charts
            type="area"
            ref="chart"
            height="250"
            :options="chartOptions"
            :series="chartSeries"
          />
        </q-card-section>
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
    </div>

    <logs-console
      class="col-12 col-lg-8 col-md-6"
      @reconnect="processLog"
      :logs="logs"
      :connected="!!logConnection"
      height="100%"
    />
  </q-page>
</template>

<script setup lang="ts">
import { api } from 'src/boot/axios';
import type { SystemStatus } from 'src/api';
import { useQuasar } from 'quasar';
import { onBeforeUnmount, onMounted, watch, ref } from 'vue';
import VueApexCharts from 'vue3-apexcharts';
import type { VueApexChartsComponent } from 'vue3-apexcharts';
import LogsConsole from 'src/components/LogsConsole.vue';

const $q = useQuasar();

const status = ref<SystemStatus>(),
  updateInterval = ref<number>(2000),
  logs = ref<string[]>([]),
  logConnection = ref<WebSocket>();

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
      range: 1.5 * 60 * 1000,
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

async function processLog() {
  const { data } = await api.systemLogsHistoryApiLogsGet();
  logs.value = data;

  logConnection.value?.close();
  const wsUrl = new URL('api/logs', location.href);
  wsUrl.protocol = wsUrl.protocol === 'https:' ? 'wss:' : 'ws:';

  logConnection.value = new WebSocket(wsUrl.href);
  logConnection.value.onmessage = ({ data }) => logs.value.push(data as string);
  logConnection.value.onclose = () => (logConnection.value = undefined);
}

onMounted(() => {
  void updateStatus();
  void processLog();
});

onBeforeUnmount(() => {
  window.clearTimeout(updateTimer);
  logConnection.value?.close();
});

watch(
  () => $q.dark.isActive,
  () =>
    void chart.value?.updateOptions({
      theme: { mode: $q.dark.isActive ? 'dark' : 'light' },
    }),
  {
    immediate: true,
  }
);
</script>
<style scoped lang="scss">
@import '@fontsource/dseg14/index.css';

.digit-display {
  font-family: DSEG14;
  font-size: larger;
  text-shadow: $cyan 1px 2px 3px;
}

.card-title {
  background-image: linear-gradient(90deg, $primary 0%, transparent 50%);
  color: white;
}
</style>
