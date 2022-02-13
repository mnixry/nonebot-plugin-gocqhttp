<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="toggleLeftDrawer" />
        <q-separator spaced vertical />
        <q-btn icon="home" to="/" flat dense round />
        <q-toolbar-title> NoneBot Plugin Go-CQHTTP </q-toolbar-title>
        <q-btn
          :icon="$q.dark.isActive ? 'dark_mode' : 'light_mode'"
          @click="$q.dark.toggle"
          flat
          dense
          round
        />
        <q-separator spaced vertical />
        <q-btn push icon="info" flat dense round>
          <q-popup-proxy>
            <q-card class="shadow q-pa-md">
              <div class="text-h6">关于</div>
              <q-banner class="text-body1" outline="grey">
                本插件基于<a href="https://github.com/Mrs4s/go-cqhttp">
                  Mrs4s/go-cqhttp
                </a>
                以及<a href="https://github.com/nonebot/nonebot2">
                  nonebot/nonebot2
                </a>
                进行开发
                <br />
                以<a
                  href="https://github.com/mnixry/nonebot-plugin-gocqhttp/blob/main/LICENSE"
                >
                  AGPL-3.0开源许可 </a
                >发布, 请在使用时遵守开源许可条款
                <q-separator spaced />
                <div class="text-grey">
                  前端界面由 Quasar v{{ $q.version }} 强力驱动
                </div>
              </q-banner>
            </q-card>
          </q-popup-proxy>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header> 帐号选择 </q-item-label>
        <AccountSelector />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view v-slot="{ Component }" :key="$route.fullPath">
        <transition
          appear
          enter-active-class="animated fadeIn"
          leave-active-class="animated fadeOut"
        >
          <component :is="Component" />
        </transition>
      </router-view>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import AccountSelector from 'components/AccountSelector.vue';
import { ref } from 'vue';
import { useRoute } from 'vue-router';

const $route = useRoute();

const leftDrawerOpen = ref(true);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>
