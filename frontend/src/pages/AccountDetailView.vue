<template>
  <q-page class="row q-pa-md justify-center">
    <div class="row col-12 col-md-4">
      <q-card class="col-12 column justify-between">
        <q-card-section class="row items-center justify-start q-gutter-md">
          <q-avatar>
            <q-img :src="`https://q1.qlogo.cn/g?b=qq&nk=${uin}&s=640`" />
          </q-avatar>
          <div class="text-h5">进程状态</div>
          <q-space />
          <q-chip color="green">
            <q-icon name="person" />帐号: {{ uin }}
          </q-chip>
        </q-card-section>

        <q-slide-transition>
          <q-card-section v-if="status" class="row justify-center items-center">
            <running-process-status
              v-if="status.status == 'running' && status.details"
              :status="status.details"
            />
            <div v-else-if="status.details">
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
                  <q-img width="30vh" :src="status.qr_uri" />
                </q-popup-proxy>
              </q-btn>
            </q-slide-transition>

            <q-card-actions>
              <q-btn
                flat
                color="red"
                icon="stop"
                @click="stopProcess"
                label="停止"
              />
              <q-btn
                flat
                color="green"
                icon="play_arrow"
                @click="startProcess"
                label="启动"
              />
            </q-card-actions>
          </q-card-section>
        </q-slide-transition>

        <q-card-actions class="row justify-center q-gutter-sm">
          <q-btn
            flat
            color="primary"
            icon="refresh"
            @click="updateStatus"
            label="刷新"
          />
          <q-btn
            flat
            color="secondary"
            label="修改配置"
            icon="settings"
            :to="`/accounts/${uin}/config`"
          />
          <q-btn
            flat
            color="accent"
            label="修改设备"
            icon="smartphone"
            :to="`/accounts/${uin}/device`"
          />
        </q-card-actions>
      </q-card>
      <message-sender class="col-12 shadow" :uin="uin" />
    </div>
    <logs-console
      class="col-12 col-md-8"
      @reconnect="processLog"
      :logs="logs"
      :connected="!!logConnection"
    >
      <template v-slot:top-trailing>
        <q-checkbox
          v-model="enableInput"
          checked-icon="menu_open"
          unchecked-icon="menu"
          color="secondary"
        />
      </template>
      <template v-slot:top>
        <q-slide-transition>
          <q-card-section v-show="enableInput">
            <q-input v-model="stdinInput" filled dense label="传入文字到进程">
              <template v-slot:after>
                <q-btn
                  icon="input"
                  flat
                  color="accent"
                  round
                  @click="sendStdin"
                />
              </template>
            </q-input>
          </q-card-section>
        </q-slide-transition>
      </template>
    </logs-console>
  </q-page>
</template>
<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue';
import { useQuasar } from 'quasar';

import { api } from 'boot/axios';
import type { ProcessInfo, ProcessLog } from 'src/api';

import RunningProcessStatus from 'components/RunningProcessStatus.vue';
import LogsConsole from 'components/LogsConsole.vue';
import MessageSender from 'src/components/MessageSender.vue';

const $q = useQuasar();

const props = defineProps<{ uin: number }>(),
  status = ref<ProcessInfo>(),
  logs = ref<ProcessLog[]>([]),
  logConnection = ref<WebSocket>(),
  enableInput = ref(false),
  stdinInput = ref('');

async function updateStatus() {
  logConnection.value?.send('heartbeat');
  try {
    $q.loadingBar.start();
    const { data } = await api.processStatusApiUinProcessStatusGet(props.uin);
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
    await api.processStopApiUinProcessDelete(props.uin);
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
    await api.processStartApiUinProcessPut(props.uin);
    await updateStatus();
  } catch (err) {
    console.error(err);
  } finally {
    $q.loading.hide();
  }
}

async function sendStdin() {
  try {
    $q.loading.show();
    await api.processInputLineApiUinProcessLogsPost(props.uin, {
      input: stdinInput.value,
    });
  } catch (err) {
    console.error(err);
  } finally {
    $q.loading.hide();
  }
}

async function processLog() {
  const { data } = await api.processLogsHistoryApiUinProcessLogsGet(props.uin);
  logs.value = data;

  logConnection.value?.close();

  const wsUrl = new URL(`api/${props.uin}/process/logs`, location.href);
  wsUrl.protocol = wsUrl.protocol === 'https:' ? 'wss:' : 'ws:';

  logConnection.value = new WebSocket(wsUrl.href);
  logConnection.value.onmessage = ({ data }) =>
    logs.value.push(JSON.parse(data as string) as ProcessLog);
  logConnection.value.onclose = () => (logConnection.value = undefined);
}

const updateTimer = window.setInterval(() => void updateStatus(), 3000);

watch(
  () => props.uin,
  async () => {
    status.value = undefined;
    logs.value = [];
    try {
      $q.loading.show();
      await updateStatus();
      await processLog();
    } finally {
      $q.loading.hide();
    }
  },
  { immediate: true }
);

onBeforeUnmount(() => {
  window.clearInterval(updateTimer);
  logConnection.value?.close();
});

void updateStatus();
</script>
