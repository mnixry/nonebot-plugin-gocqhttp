import {
  RouteRecordRaw,
  RouteLocationNormalized,
  RouteParams,
} from 'vue-router';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Constructor<T = any> = new (...args: any[]) => T;
type TransformMap<T> = {
  [K in keyof T]: T[K] extends Constructor<infer S> ? S : never;
};

const transform =
  <T extends Record<string, Constructor>>(fields: T) =>
  (to: RouteLocationNormalized) =>
    Object.entries(to.params)
      .map(([key, value]) => ({
        [key]: (fields[key]
          ? new fields[key](value)
          : value) as TransformMap<T>[typeof key],
      }))
      .reduce((acc, cur) => ({ ...acc, ...cur }), {}) as TransformMap<T> &
      RouteParams;

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '/', component: () => import('pages/IndexView.vue') },
      {
        path: '/accounts/add',
        component: () => import('pages/AccountAddView.vue'),
      },
      {
        path: '/accounts/:uin(\\d+)',
        component: () => import('pages/AccountDetailView.vue'),
        props: transform({ uin: Number }),
      },
      {
        path: '/accounts/:uin(\\d+)/config',
        component: () => import('pages/AccountConfigEditorView.vue'),
        props: transform({ uin: Number }),
      },
      {
        path: '/accounts/:uin(\\d+)/device',
        component: () => import('pages/AccountDeviceEditorView.vue'),
        props: transform({ uin: Number }),
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('src/pages/NotFoundView.vue'),
  },
];

export default routes;
