import { boot } from 'quasar/wrappers';
import _axios, { AxiosInstance } from 'axios';
import { ApiApi as Api } from 'src/api';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
    $api: Api;
  }
}

const axios = _axios.create();

export const api = new Api(undefined, '', axios);

export default boot(({ app }) => {
  app.config.globalProperties.$axios = axios;
  app.config.globalProperties.$api = api;
});
