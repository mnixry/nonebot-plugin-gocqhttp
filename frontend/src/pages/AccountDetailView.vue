<template>
  <q-page class="row q-pa-md justify-center">
    <div class="row col-12 col-md-4">
      <q-card class="col-12 shadow">
        <q-card-section class="q-pa-md row items-center justify-start">
          <q-avatar>
            <q-img :src="`https://q1.qlogo.cn/g?b=qq&nk=${uin}&s=640`" />
          </q-avatar>
          <div class="text-h5 q-px-md">进程状态</div>
          <q-chip color="green">
            <q-icon name="person" />帐号: {{ uin }}
          </q-chip>
        </q-card-section>
        <q-separator />

        <q-slide-transition>
          <q-card-section v-if="status" class="row justify-center items-center">
            <running-process-status
              v-if="'pid' in status.details"
              :status="status.details"
            />
            <div v-else>
              <q-chip>
                <q-avatar icon="error" color="red" text-color="white" />
                <strong>退出代码:</strong><code>{{ status.details.code }}</code>
              </q-chip>
            </div>

            <div class="row justify-center">
              <q-chip outline color="green">
                <q-icon name="description" color="accent" />
                日志条数<code>{{ status.total_logs }}条</code>
              </q-chip>
              <q-chip outline color="red">
                <q-icon name="restart_alt" color="accent" />
                重启次数<code>{{ status.restarts }}次</code>
              </q-chip>
            </div>

            <q-slide-transition v-if="status.qr_uri" class="q-ma-md">
              <q-btn push icon="qr_code" color="accent">
                显示登录二维码
                <q-popup-proxy>
                  <q-img width="40vh" :src="status.qr_uri" />
                </q-popup-proxy>
              </q-btn>
            </q-slide-transition>
          </q-card-section>
        </q-slide-transition>

        <q-separator />
        <q-card-actions class="justify-center">
          <q-btn flat color="primary" icon="refresh" @click="updateStatus"
            >刷新</q-btn
          >
          <q-btn
            flat
            color="red"
            icon="stop"
            v-if="status?.status == 'running'"
            @click="stopProcess"
            >停止</q-btn
          >
          <q-btn
            flat
            color="green"
            icon="play_arrow"
            v-else
            @click="startProcess"
            >启动</q-btn
          >
        </q-card-actions>
      </q-card>
      <message-sender class="col-12 shadow" :uin="uin" />
    </div>
    <q-card class="col-12 col-md-8 q-pa-md">
      <div class="text-body1 text-grey"><strong>进程日志</strong></div>
      <q-separator spaced />
      <logs-console :logs="logs" />
    </q-card>
  </q-page>
</template>
<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue';
import RunningProcessStatus from 'components/RunningProcessStatus.vue';
import LogsConsole from 'components/LogsConsole.vue';
import type { ProcessInfo, ProcessLog } from 'src/api';
import MessageSender from 'src/components/MessageSender.vue';
import { useQuasar } from 'quasar';
import { useRoute } from 'vue-router';
import { api } from 'src/boot/axios';

const $q = useQuasar(),
  $route = useRoute();

const uin = ref<number>(+$route.params.uin);

const status = ref<ProcessInfo>(),
  logs = ref<ProcessLog[]>([]);

let logWebsocket = undefined as WebSocket | undefined;

async function updateStatus() {
  logWebsocket?.send('heartbeat');
  try {
    $q.loadingBar.start();
    const { data } = await api.processStatusApiUinProcessStatusGet(uin.value);
    status.value = data;
  } catch (err) {
    console.error(err);
  } finally {
    $q.loadingBar.stop();
  }
}

async function stopProcess() {
  try {
    $q.loading.show();
    await api.processStopApiUinProcessDelete(uin.value);
    await updateStatus();
  } catch (err) {
    console.error(err);
  } finally {
    $q.loading.hide();
  }
}

async function startProcess() {
  try {
    $q.loading.show();
    await api.processStartApiUinProcessPut(uin.value);
    await updateStatus();
  } catch (err) {
    console.error(err);
  } finally {
    $q.loading.hide();
  }
}

async function logHistory() {
  try {
    const { data } = await api.processLogsHistoryApiUinProcessLogsGet(
      uin.value
    );
    logs.value = data;
  } catch (err) {
    console.error(err);
  } finally {
  }
}

function logRealtime() {
  if (Number.isNaN(uin)) return;

  logWebsocket?.close();

  const wsUrl = new URL(`api/${uin.value}/process/logs`, location.href);
  wsUrl.protocol = wsUrl.protocol === 'https:' ? 'wss:' : 'ws:';

  logWebsocket = new WebSocket(wsUrl.href);
  logWebsocket.onmessage = ({ data }) => {
    const log = JSON.parse(<string>data) as ProcessLog;
    logs.value.push(log);
  };
  logWebsocket.onclose = () => {
    logWebsocket = undefined;
  };
}

void updateStatus();
const updateTimer = window.setInterval(() => void updateStatus(), 3000);

watch(
  () => $route.params,
  async () => {
    uin.value = +$route.params.uin;
    status.value = undefined;
    logs.value = [];
    try {
      $q.loading.show();
      await updateStatus();
      await logHistory();
      logRealtime();
    } finally {
      $q.loading.hide();
    }
  },
  { immediate: true }
);

onBeforeUnmount(() => {
  window.clearInterval(updateTimer);
  logWebsocket?.close();
});
</script>
