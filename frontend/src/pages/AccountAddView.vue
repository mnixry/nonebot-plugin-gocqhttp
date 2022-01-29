<template>
  <q-page class="row justify-center">
    <q-card
      class="col-12 col-xs-8 col-sm-6 col-md-4 shadow q-pa-md self-center"
    >
      <q-card-section>
        <div class="text-h5">
          <q-icon name="person" color="accent" />添加帐号
        </div>
      </q-card-section>
      <q-separator />
      <q-form
        autocorrect="off"
        autocapitalize="off"
        autocomplete="off"
        spellcheck="false"
        @submit="addAccount"
        @reset="clearForm"
      >
        <q-card-section class="q-gutter-md">
          <q-input
            v-model.number="uin"
            type="number"
            autofocus
            filled
            counter
            clearable
            label="QQ号"
            :rules="[(v) => Number.isInteger(v) || '请输入QQ号']"
          >
            <template v-slot:prepend><q-icon name="badge" /></template>
          </q-input>
          <q-input
            v-model="password"
            type="password"
            counter
            outlined
            clearable
            label="密码"
            hint="留空以使用二维码登录"
          >
            <template v-slot:prepend><q-icon name="password" /></template>
          </q-input>
          <q-select
            v-model="protocol"
            :options="protocols"
            inline
            label="登录设备类型"
          >
            <template v-slot:before><q-icon name="devices" /></template>
          </q-select>
        </q-card-section>
        <q-separator />
        <q-card-actions class="justify-center">
          <q-btn flat color="positive" type="submit" icon="add">提交</q-btn>
          <q-btn flat color="negative" type="reset" icon="clear">清除</q-btn>
        </q-card-actions>
      </q-form>
    </q-card>
  </q-page>
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import { AccountProtocol } from 'src/api';

const PROTOCOL_MAP = {
  iPad: AccountProtocol.NUMBER_0,
  Phone: AccountProtocol.NUMBER_1,
  Mac: AccountProtocol.NUMBER_2,
  Watch: AccountProtocol.NUMBER_3,
  QiDian: AccountProtocol.NUMBER_4,
};

export default defineComponent({
  data: () => ({
    uin: null as null | number,
    password: null as null | string,
    protocol: null as null | AccountProtocol,
  }),
  computed: {
    protocols() {
      return Object.entries(PROTOCOL_MAP).map(([label, value]) => ({
        label,
        value,
      }));
    },
  },
  methods: {
    async addAccount() {
      if (!this.uin) return;
      try {
        this.$q.loading.show();
        await this.$api.createAccountApiUinPut(this.uin, {
          password: this.password ?? undefined,
          device_extra:
            this.protocol !== null
              ? {
                  protocol: this.protocol,
                }
              : undefined,
        });
        await this.$router.push('/');
      } catch (err) {
        this.$q.notify({
          color: 'negative',
          message: (err as Error).message,
        });
      } finally {
        this.$q.loading.hide();
      }
    },
    clearForm() {
      this.uin = null;
      this.password = null;
      this.protocol = null;
    },
  },
});
</script>
