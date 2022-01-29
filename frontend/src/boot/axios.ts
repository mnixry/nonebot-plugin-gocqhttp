import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance } from 'axios';
import { ApiApi as Api } from 'src/api';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
    $api: Api;
  }
}

export const api = new Api(undefined, '.');

export default boot(({ app }) => {
  app.config.globalProperties.$axios = axios;
  app.config.globalProperties.$api = api;
});
