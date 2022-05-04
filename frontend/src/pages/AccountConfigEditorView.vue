<template>
  <q-page class="row q-pa-md justify-center">
    <q-card class="shadow col-12" style="height: calc(100vh - 5rem)">
      <q-card-section class="row justify-start items-center">
        <q-btn
          @click="$router.back"
          flat
          label="返回"
          color="grey"
          icon="arrow_back"
        />
        <div class="text-h5">编辑配置文件</div>
      </q-card-section>
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
          language="yaml"
          style="height: 70vh"
          :theme="$q.dark.isActive ? 'vs-dark' : 'vs'"
        />
        <q-inner-loading :showing="loading" />
      </q-card-section>
    </q-card>
  </q-page>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useQuasar } from 'quasar';

import ConfigFileEditor from 'src/components/ConfigFileEditor.vue';
import { api } from 'boot/axios';

const $q = useQuasar();

const props = defineProps<{ uin: number }>(),
  content = ref<string>(),
  loading = ref(true);

async function loadConfig() {
  try {
    loading.value = true;
    const { data } = await api.accountConfigReadApiUinConfigGet(props.uin);
    content.value = data.content;
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

    const { data } = await api.accountConfigWriteApiUinConfigPatch(props.uin, {
      content: content.value,
    });
    content.value = data.content;

    $q.notify({ message: '配置文件修改成功', color: 'positive' });
  } catch (err) {
    $q.notify({ message: '配置文件修改失败', color: 'negative' });
  } finally {
    loading.value = false;
  }
}

async function deleteConfig() {
  try {
    loading.value = true;
    await api.accountConfigDeleteApiUinConfigDelete(props.uin);
    await loadConfig();
    $q.notify({ message: '配置文件删除成功', color: 'positive' });
  } catch {
    $q.notify({ message: '配置文件删除失败', color: 'negative' });
  } finally {
    loading.value = false;
  }
}

onMounted(loadConfig);
</script>
