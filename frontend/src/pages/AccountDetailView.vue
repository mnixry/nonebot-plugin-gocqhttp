<template>
  <q-page class="row q-pa-md justify-center">
    <q-card class="col-12 col-md-4 shadow">
      <q-card-section class="q-pa-md row items-center justify-start">
        <q-avatar>
          <q-img :src="`https://q1.qlogo.cn/g?b=qq&nk=${uin}&s=640`" />
        </q-avatar>
        <div class="text-h5 q-px-md">进程状态</div>
        <q-chip color="green"> <q-icon name="person" />帐号: {{ uin }} </q-chip>
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
        <q-btn flat color="green" icon="play_arrow" v-else @click="startProcess"
          >启动</q-btn
        >
      </q-card-actions>
    </q-card>
    <q-card class="col-12 col-md-8 q-pa-md">
      <div class="text-body1 text-grey"><strong>进程日志</strong></div>
      <q-separator spaced />
      <logs-console :logs="logs" />
    </q-card>
  </q-page>
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import RunningProcessStatus from 'components/RunningProcessStatus.vue';
import LogsConsole from 'components/LogsConsole.vue';
import { ProcessInfo, ProcessLog } from 'src/api';

export default defineComponent({
  data: () => ({
    updateTimer: null as number | null,
    logWebsocket: null as WebSocket | null,
    status: null as ProcessInfo | null,
    logs: [] as ProcessLog[],
  }),
  components: { RunningProcessStatus, LogsConsole },
  computed: {
    uin(): number {
      return +this.$route.params.uin;
    },
  },
  methods: {
    async updateStatus() {
      if (this.logWebsocket) this.logWebsocket.send('heartbeat');
      try {
        this.$q.loadingBar.start();
        const { data: status } =
          await this.$api.processStatusApiUinProcessStatusGet(this.uin);
        this.status = status;
      } catch (err) {
        console.error(err);
      } finally {
        this.$q.loadingBar.stop();
      }
    },
    async stopProcess() {
      try {
        this.$q.loading.show();
        await this.$api.processStopApiUinProcessDelete(this.uin);
        await this.updateStatus();
      } catch (err) {
        console.error(err);
      } finally {
        this.$q.loading.hide();
      }
    },
    async startProcess() {
      try {
        this.$q.loading.show();
        await this.$api.processStartApiUinProcessPut(this.uin);
        await this.updateStatus();
      } catch (err) {
        console.error(err);
      } finally {
        this.$q.loading.hide();
      }
    },
    async logHistory() {
      try {
        const { data: logs } =
          await this.$api.processLogsHistoryApiUinProcessLogsGet(this.uin);
        this.logs = logs;
      } catch (err) {
        console.error(err);
      } finally {
      }
    },
    logRealtime() {
      if (this.logWebsocket) this.logWebsocket.close();
      if (Number.isNaN(this.uin)) return;
      const wsUrl = new URL(`api/${this.uin}/process/logs`, location.href);
      wsUrl.protocol = wsUrl.protocol === 'https:' ? 'wss:' : 'ws:';

      this.logWebsocket = new WebSocket(wsUrl.href);
      this.logWebsocket.onmessage = ({ data }) => {
        const log = JSON.parse(<string>data) as ProcessLog;
        this.logs.push(log);
      };
      this.logWebsocket.onclose = () => {
        this.logWebsocket = null;
      };
    },
  },
  created() {
    this.updateTimer = window.setInterval(() => void this.updateStatus(), 3000);

    this.$watch(
      () => this.$route.params,
      async () => {
        this.status = null;
        this.logs = [];
        try {
          this.$q.loading.show();
          await this.updateStatus();
          await this.logHistory();
          this.logRealtime();
        } finally {
          this.$q.loading.hide();
        }
      },
      { immediate: true }
    );
  },
  beforeUnmount() {
    if (this.updateTimer) window.clearInterval(this.updateTimer);
    if (this.logWebsocket) this.logWebsocket.close();
  },
});
</script>
