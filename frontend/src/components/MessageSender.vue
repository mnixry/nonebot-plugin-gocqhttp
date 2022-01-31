<template>
  <q-card>
    <q-tabs v-model="sendType" active-color="primary">
      <q-tab name="group" label="群聊" icon="groups"></q-tab>
      <q-tab name="friend" label="好友" icon="chat"></q-tab>
    </q-tabs>
    <q-separator />
    <q-tab-panels v-model="sendType" animated>
      <q-tab-panel name="group" class="row justify-evenly">
        <q-select
          class="col-8"
          v-model="selectedGroup"
          filled
          @filter="
            (val, update, abort) =>
              getGroupList().then((result) =>
                update(() => (groupList = result))
              )
          "
          :options="groupList"
          option-label="group_name"
          option-value="group_id"
          label="选择群聊"
          map-options
          emit-value
          ><template v-slot:option="scope">
            <q-item v-bind="scope.itemProps">
              <q-item-section avatar>
                <q-avatar>
                  <q-img
                    :src="`http://p.qlogo.cn/gh/${scope.opt.group_id}/${scope.opt.group_id}/100/`"
                  />
                </q-avatar>
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ scope.opt.group_name }}</q-item-label>
                <q-item-label caption>{{ scope.opt.group_id }}</q-item-label>
              </q-item-section>
            </q-item>
          </template>
          <template v-slot:no-option>
            <q-item>
              <q-item-section class="text-grey">没有群</q-item-section>
            </q-item>
          </template>
        </q-select>
        <q-btn
          class="col-2"
          flat
          icon="send"
          color="indigo"
          :disable="!(message && selectedGroup)"
          @click="sendMsg(message!, { group_id: selectedGroup! }).then(() => { message = undefined })"
        />
      </q-tab-panel>
      <q-tab-panel name="friend" class="row justify-evenly">
        <q-select
          class="col-8"
          v-model="selectedFriend"
          filled
          @filter="
            (val, update, abort) =>
              getFriendList().then((result) =>
                update(() => (friendList = result))
              )
          "
          :options="friendList"
          option-label="nickname"
          option-value="user_id"
          label="选择好友"
          map-options
          emit-value
          ><template v-slot:option="scope">
            <q-item v-bind="scope.itemProps">
              <q-item-section avatar>
                <q-avatar>
                  <q-img
                    :src="`https://q1.qlogo.cn/g?b=qq&nk=${scope.opt.user_id}&s=640`"
                  />
                </q-avatar>
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ scope.opt.nickname }}</q-item-label>
                <q-item-label caption>{{ scope.opt.user_id }}</q-item-label>
              </q-item-section>
            </q-item>
          </template>
          <template v-slot:no-option>
            <q-item>
              <q-item-section class="text-grey">没有好友</q-item-section>
            </q-item>
          </template>
        </q-select>
        <q-btn
          class="col-2"
          flat
          icon="send"
          color="deep-orange"
          :disable="!(message && selectedFriend)"
          @click="sendMsg(message!, { user_id: selectedFriend! }).then(() => { message = undefined})"
        />
      </q-tab-panel>
    </q-tab-panels>
    <q-card-section>
      <q-input
        v-model="message"
        style="height: 15vh"
        autogrow
        outlined
        label="消息正文"
        :rules="[(v) => !!String(v).trim() || '请输入消息正文']"
      ></q-input>
    </q-card-section>
  </q-card>
</template>
<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import { api } from 'src/boot/axios';
import { ref, UnwrapRef } from 'vue';

const props = defineProps({ uin: { type: Number, required: true } });

const sendType = ref<'group' | 'friend'>('group');
const message = ref<string>();

const groupList = ref<{ user_id: number; nickname: string }[]>([]);
const selectedGroup = ref<number>();

const friendList = ref<{ user_id: number; nickname: string }[]>([]);
const selectedFriend = ref<number>();

async function getGroupList() {
  const { data } = await api.accountApiApiUinApiPost(
    props.uin,
    'get_group_list',
    { no_cache: true }
  );
  return data as UnwrapRef<typeof groupList>;
}

async function getFriendList() {
  const { data } = await api.accountApiApiUinApiPost(
    props.uin,
    'get_friend_list',
    { no_cache: true }
  );
  return data as UnwrapRef<typeof friendList>;
}

async function sendMsg(
  message: string,
  options: { group_id: number } | { user_id: number }
) {
  const { data } = await api.accountApiApiUinApiPost(props.uin, 'send_msg', {
    message,
    ...options,
  });
  return data as { message_id: number };
}
</script>
