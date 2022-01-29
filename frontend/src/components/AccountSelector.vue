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
      v-for="account in accounts"
      :key="account"
      :to="`/accounts/${account}`"
    >
      <q-item-section avatar>
        <q-avatar>
          <q-img :src="`https://q1.qlogo.cn/g?b=qq&nk=${account}&s=640`" />
        </q-avatar>
      </q-item-section>
      <q-item-section>{{ account }}</q-item-section>
      <q-item-section side>
        <q-btn
          flat
          color="grey"
          icon="delete"
          @click="deleteAccount(account)"
        />
      </q-item-section>
    </q-item>

    <q-inner-loading :showing="loading" />
  </q-list>
</template>
<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  data: () => ({
    accounts: [] as number[],
    updateTimer: null as number | null,
    loading: false,
  }),
  methods: {
    async deleteAccount(uin: number) {
      const confirm = await new Promise<boolean>((resolve) => {
        this.$q
          .dialog({
            title: '确认删除',
            message: '确认删除该帐号？',
            ok: '确认',
            cancel: '取消',
            persistent: true,
          })
          .onOk(() => resolve(true))
          .onCancel(() => resolve(false));
      });
      if (!confirm) return;
      await this.$router.push('/');
      try {
        this.$q.loading.show();
        await this.$api.deleteAccountApiUinDelete(uin);
      } catch (e) {
        this.$q.notify({
          color: 'negative',
          message: (e as Error).message,
        });
      } finally {
        this.$q.loading.hide();
      }
    },
    async getAccounts() {
      try {
        this.loading = true;
        const { data: accounts } = await this.$api.allAccountsApiGet();
        this.accounts = accounts;
      } finally {
        this.loading = false;
      }
    },
  },
  created() {
    void this.getAccounts();
    this.updateTimer = window.setInterval(() => {
      void this.getAccounts();
    }, 10 * 1000);
  },
  beforeUnmount() {
    if (this.updateTimer) window.clearInterval(this.updateTimer);
  },
});
</script>
