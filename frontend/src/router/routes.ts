import { RouteRecordRaw } from 'vue-router';

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
        props: true,
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
