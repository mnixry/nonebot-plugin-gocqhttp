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
            autofocus
            filled
            counter
            clearable
            label="QQ号"
            :rules="[(v) => +v >= 1e4 || '请输入QQ号']"
          >
            <template v-slot:prepend><q-icon name="badge" /></template>
          </q-input>
          <q-input
            v-model="password"
            type="password"
            counter
            outlined
            :filled="(password?.length ?? 0) > 0"
            clearable
            label="密码"
            hint="手表协议可以留空以使用二维码登录"
            :rules="[
              (v) =>
                typeof v === 'string' && v.length > 0
                  ? true
                  : protocol === AccountProtocol.NUMBER_2 || '请输入密码',
            ]"
          >
            <template v-slot:prepend><q-icon name="password" /></template>
          </q-input>
          <q-select
            v-model="protocol"
            :options="protocols"
            inline
            map-options
            emit-value
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
<script setup lang="ts">
import { ref } from 'vue';
import { AccountProtocol } from 'src/api';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { api } from 'src/boot/axios';

const $q = useQuasar(),
  $router = useRouter();

const protocols = Object.entries({
  [AccountProtocol.NUMBER_0]: 'Default/Unset',
  [AccountProtocol.NUMBER_1]: 'Android Phone',
  [AccountProtocol.NUMBER_2]: 'Android Watch',
  [AccountProtocol.NUMBER_3]: 'MacOS',
  [AccountProtocol.NUMBER_4]: '企点',
  [AccountProtocol.NUMBER_5]: 'iPad',
  [AccountProtocol.NUMBER_6]: 'aPad',
}).map(([value, label]) => ({ value: +value, label }));

const uin = ref<number>(),
  password = ref<string>(),
  protocol = ref<AccountProtocol>();

async function addAccount() {
  if (!uin.value) return;
  try {
    $q.loading.show();
    await api.createAccountApiUinPut(uin.value, {
      password: password.value?.trim() ? password.value : undefined,
      protocol: protocol.value,
    });
    void $router.push(`/accounts/${uin.value}`);
  } catch (err) {
    $q.notify({
      color: 'negative',
      message: (err as Error).message,
    });
  } finally {
    $q.loading.hide();
  }
}

function clearForm() {
  uin.value = undefined;
  password.value = undefined;
  protocol.value = undefined;
}
</script>
