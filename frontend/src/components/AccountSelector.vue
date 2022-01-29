<template>
  <q-list bordered>
    <q-item clickable>
      <q-item-section>
        <q-btn flat color="primary">
          <q-icon name="add" />
          <span>添加帐号</span>
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
    </q-item>
  </q-list>
</template>
<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  data: () => ({
    accounts: [] as number[],
  }),
  async mounted() {
    const accounts = await this.$api.allAccountsApiGet();
    this.accounts = accounts.data;
  },
});
</script>
