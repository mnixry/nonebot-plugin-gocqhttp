<template>
  <q-page class="row q-pa-md justify-center">
    <q-card class="shadow col-12" style="height: calc(100vh - 5rem)">
      <q-card-section class="row items-center">
        <q-btn
          @click="$router.back"
          flat
          label="返回"
          color="grey"
          icon="arrow_back"
        />
        <div class="text-h5">编辑设备信息文件</div>
        <q-space />
        <div class="column">
          <div class="text-body">
            <a href="https://qdvc.ilharp.cc/">QDVC</a>
            导入导出
          </div>
          <div class="q-gutter-md">
            <q-btn
              class="q-ml-md"
              @click="importDialog = true"
              flat
              round
              color="primary"
              icon="login"
            />
            <q-btn
              class="q-ml-md"
              @click="exportDialog = true"
              flat
              round
              color="secondary"
              icon="logout"
            />
          </div>
        </div>
      </q-card-section>
      <q-dialog v-model="exportDialog">
        <q-card>
          <q-card-section>
            <div class="text-h6">导出 QDVC</div>
          </q-card-section>
          <q-separator />
          <q-card-section>
            <div style="max-height: 30vh; font-family: monospace">
              <q-input
                v-model="qdvcUri"
                :loading="qdvcUri.length <= 0"
                readonly
                type="textarea"
                label="QDVC分享连接"
              />
            </div>
          </q-card-section>
          <q-card-actions class="row justify-center">
            <q-btn-toggle
              v-model="qdvcEncoding"
              toggle-color="secondary"
              flat
              :options="[
                { label: 'Base64', value: 'base64' },
                { label: 'Base16384', value: 'base16384' },
              ]"
            />
            <q-btn
              @click="writeQdvcUri"
              flat
              label="复制到剪贴板"
              color="primary"
              icon="content_copy"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <q-dialog v-model="importDialog">
        <q-card>
          <q-card-section>
            <div class="text-h6">导入 QDVC</div>
          </q-card-section>
          <q-separator />
          <q-card-section>
            <div style="max-height: 30vh; font-family: monospace">
              <q-input
                v-model="qdvcUri"
                :loading="qdvcApplying"
                :disable="qdvcApplying"
                :rules="[(val) => QDVC.RE.test(val) || '不是有效的 QDVC 链接']"
                type="textarea"
                label="QDVC分享连接"
              />
            </div>
          </q-card-section>
          <q-card-actions class="row justify-center">
            <q-btn
              @click="applyQdvcUri"
              flat
              label="应用 QDVC 配置"
              color="primary"
              icon="login"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <q-separator />
      <q-card-actions class="q-gutter-md q-mx-md">
        <q-btn
          flat
          @click="updateConfig"
          color="primary"
          label="提交修改"
          icon="save"
        />
        <q-btn
          flat
          @click="loadConfig"
          color="secondary"
          label="重新加载配置文件"
          icon="refresh"
        />
        <q-btn
          flat
          @click="deleteConfig"
          color="negative"
          label="删除并重新生成配置文件"
          icon="delete"
        />
      </q-card-actions>
      <q-card-section>
        <config-file-editor
          v-if="typeof content !== 'undefined'"
          v-model="content"
          language="json"
          style="height: 70vh"
          :theme="$q.dark.isActive ? 'vs-dark' : 'vs'"
        />
        <q-inner-loading :showing="loading" />
      </q-card-section>
    </q-card>
  </q-page>
</template>
<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useQuasar } from 'quasar';

import ConfigFileEditor from 'src/components/ConfigFileEditor.vue';
import type { DeviceInfo } from 'src/api';
import { api } from 'boot/axios';
import { QDVC } from './qdvc-utils';

const $q = useQuasar();

const props = defineProps<{ uin: number }>(),
  content = ref<string>(),
  loading = ref(true),
  exportDialog = ref(false),
  importDialog = ref(false),
  qdvcUri = ref(''),
  qdvcApplying = ref(false),
  qdvcEncoding = ref<'base64' | 'base16384'>('base64');

async function loadConfig() {
  try {
    loading.value = true;
    const { data } = await api.accountDeviceReadApiUinDeviceGet(props.uin);
    content.value = JSON.stringify(data, null, 2);
  } catch {
    content.value = undefined;
  } finally {
    loading.value = false;
  }
}

async function updateConfig() {
  if (!content.value) return;
  try {
    loading.value = true;
    content.value = JSON.stringify(
      await api
        .accountDeviceWriteApiUinDevicePatch(
          props.uin,
          JSON.parse(content.value) as DeviceInfo
        )
        .then((res) => res.data),
      null,
      2
    );
    $q.notify({ message: '设备信息修改成功', color: 'positive' });
  } catch (e) {
    $q.notify({
      message: `设备信息修改失败: ${(e as Error).message}`,
      color: 'negative',
    });
  } finally {
    loading.value = false;
  }
}

async function deleteConfig() {
  try {
    loading.value = true;
    await api.accountConfigDeleteApiUinConfigDelete(props.uin);
    await loadConfig();
    $q.notify({ message: '设备信息删除成功', color: 'positive' });
  } catch {
    $q.notify({ message: '设备信息删除失败', color: 'negative' });
  } finally {
    loading.value = false;
  }
}

onMounted(loadConfig);

watch(exportDialog, async (val) => {
  if (val)
    try {
      qdvcUri.value = '';
      const device = await api
          .accountDeviceReadApiUinDeviceGet(props.uin)
          .then(({ data }) => JSON.stringify(data)),
        session = await api
          .accountSessionReadApiUinSessionGet(props.uin)
          .then(({ data }) => QDVC.decodeBase64(data.base64_content, false))
          .catch(() => undefined);
      qdvcUri.value = QDVC.stringify({ device, session }, qdvcEncoding.value);
    } catch (e) {
      $q.notify({
        message: `设备信息导入失败: ${(e as Error).message}`,
        color: 'negative',
      });
    }
  else qdvcUri.value = '';
});

async function writeQdvcUri() {
  if (navigator.clipboard) {
    await navigator.clipboard.writeText(qdvcUri.value);
    $q.notify({ message: '已复制到剪贴板', color: 'positive' });
  }
}

async function applyQdvcUri() {
  const parsed = QDVC.parse(qdvcUri.value);
  if (!parsed) return;
  try {
    qdvcApplying.value = true;
    if (parsed.device)
      await api.accountDeviceWriteApiUinDevicePatch(
        props.uin,
        JSON.parse(parsed.device) as DeviceInfo
      );
    if (parsed.session)
      await api.accountSessionWriteApiUinSessionPatch(props.uin, {
        base64_content: QDVC.encodeBase64(parsed.session),
      });
    $q.notify({ message: '设备信息导入成功', color: 'positive' });
  } catch (e) {
    $q.notify({
      message: `设备信息导入失败: ${(e as Error).message}`,
      color: 'negative',
    });
  } finally {
    qdvcApplying.value = false;
  }
}

watch(qdvcEncoding, (val) => {
  qdvcUri.value = QDVC.parse(qdvcUri.value)
    ? QDVC.stringify(QDVC.parse(qdvcUri.value)!, val)
    : '';
});
</script>
