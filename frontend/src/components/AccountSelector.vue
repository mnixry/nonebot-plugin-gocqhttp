<template>
  <q-list bordered>
    <q-item>
      <q-item-section>
        <q-btn flat color="primary" to="/accounts/add">
          <q-icon name="add" />添加帐号
        </q-btn>
      </q-item-section>
      <q-item-section>
        <q-btn flat @click="getAccounts">
          <q-icon name="refresh" />刷新列表
        </q-btn>
      </q-item-section>
    </q-item>
    <q-separator />
    <q-item
      clickable
      exact
      v-for="account in accounts"
      :key="account.uin"
      :to="`/accounts/${account.uin}`"
    >
      <q-item-section avatar>
        <q-avatar>
          <q-img :src="`https://q1.qlogo.cn/g?b=qq&nk=${account.uin}&s=640`" />
        </q-avatar>
      </q-item-section>
      <q-item-section>
        <q-item-label outline v-if="account.nickname">
          {{ account.nickname }}
        </q-item-label>
        <q-item-label>
          <strong>{{ account.uin }}</strong>
        </q-item-label>
        <q-item-label caption class="q-gutter-xs">
          <span v-if="account.predefined" class="text-orange">
            来自配置文件
          </span>
          <span v-else class="text-green"> 手动添加 </span>
          <span v-if="!account.process_connected" class="text-accent">
            <span v-if="!account.process_created">进程未创建</span>
            <span v-if="!account.process_running">进程停止</span>
          </span>
        </q-item-label>
      </q-item-section>
      <q-item-section side>
        <q-btn
          flat
          color="grey"
          icon="delete"
          :disable="account.predefined"
          @click="deleteAccount(account.uin)"
        />
      </q-item-section>
    </q-item>

    <q-inner-loading :showing="loading" />
  </q-list>
</template>
<script setup lang="ts">
import { useQuasar } from 'quasar';
import type { AccountListItem } from 'src/api';
import { api } from 'boot/axios';
import { onBeforeUnmount, ref } from 'vue';
import { useRouter } from 'vue-router';

const $q = useQuasar(),
  $router = useRouter();

const accounts = ref<AccountListItem[]>([]),
  loading = ref(false);

async function deleteAccount(uin: number) {
  const confirm = await new Promise<boolean | undefined>((resolve) => {
    $q.dialog({
      title: '确认删除',
      message: `确认删除帐号${uin}?`,
      options: {
        model: [],
        type: 'checkbox',
        items: [{ label: '同时删除相关文件', value: true, color: 'negative' }],
      },
    })
      .onOk(([withFile]) => resolve(!!withFile))
      .onCancel(() => resolve(undefined));
  });
  if (typeof confirm === 'undefined') return;

  await $router.push('/');
  try {
    $q.loading.show();
    await api.deleteAccountApiUinDelete(uin, confirm);
  } catch (e) {
    $q.notify({
      color: 'negative',
      message: (e as Error).message,
    });
  } finally {
    $q.loading.hide();
  }
}

async function getAccounts() {
  try {
    loading.value = true;
    const { data } = await api.allAccountsApiAccountsGet();
    accounts.value = data;
  } finally {
    loading.value = false;
  }
}

void getAccounts();
const updateTimer = window.setInterval(() => void getAccounts(), 5 * 1000);
onBeforeUnmount(() => window.clearInterval(updateTimer));
</script>
