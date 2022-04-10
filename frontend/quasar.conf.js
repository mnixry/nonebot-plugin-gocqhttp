/*
 * This file runs in a Node context (it's NOT transpiled by Babel), so use only
 * the ES6 features that are supported by your Node version. https://node.green/
 */

// Configuration for your app
// https://quasar.dev/quasar-cli/quasar-conf-js

/* eslint-env node */
/* eslint-disable @typescript-eslint/no-var-requires */
const { configure } = require('quasar/wrappers');
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

const fs = require('fs');
const path = require('path');

/**
 * @param {string} src
 * @param {string} dest
 */
function copyFolderRecursively(src, dest, cleanDest = true) {
  console.log('Copy directory', src, 'to', dest);

  if (cleanDest) fs.rmSync(dest, { recursive: true, force: true });
  if (!fs.existsSync(dest)) fs.mkdirSync(dest);

  fs.readdirSync(src).forEach((file) => {
    const srcFile = path.join(src, file),
      destFile = path.join(dest, file),
      srcStat = fs.statSync(srcFile);
    if (srcStat.isDirectory()) {
      fs.mkdirSync(destFile);
      copyFolderRecursively(srcFile, destFile);
    } else {
      fs.copyFileSync(srcFile, destFile);
    }
  });
}

module.exports = configure(function (ctx) {
  return {
    // https://quasar.dev/quasar-cli/supporting-ts
    supportTS: {
      tsCheckerConfig: {
        eslint: {
          enabled: true,
          files: './src/**/*.{ts,tsx,js,jsx,vue}',
        },
      },
    },

    // https://quasar.dev/quasar-cli/prefetch-feature
    preFetch: true,

    // app boot file (/src/boot)
    // --> boot files are part of "main.js"
    // https://quasar.dev/quasar-cli/boot-files
    boot: ['axios'],

    // https://quasar.dev/quasar-cli/quasar-conf-js#Property%3A-css
    css: ['app.scss'],

    // https://github.com/quasarframework/quasar/tree/dev/extras
    extras: [
      // 'ionicons-v4',
      // 'mdi-v5',
      // 'fontawesome-v5',
      // 'eva-icons',
      // 'themify',
      // 'line-awesome',
      // 'roboto-font-latin-ext', // this or either 'roboto-font', NEVER both!

      'roboto-font', // optional, you are not bound to it
      'material-icons', // optional, you are not bound to it
    ],

    // Full list of options: https://quasar.dev/quasar-cli/quasar-conf-js#Property%3A-build
    build: {
      vueRouterMode: 'hash', // available values: 'hash', 'history'

      // transpile: false,
      // publicPath: '/',

      // Add dependencies for transpiling with Babel (Array of string/regex)
      // (from node_modules, which are by default not transpiled).
      // Applies only if "transpile" is set to true.
      // transpileDependencies: [],

      // rtl: true, // https://quasar.dev/options/rtl-support
      // preloadChunks: true,
      showProgress: true,
      // gzip: true,
      analyze: {
        openAnalyzer: false,
        analyzerMode: 'static',
        defaultSizes: 'gzip',
      },

      // Options below are automatically set depending on the env, set them if you want to override
      extractCSS: true,
      minify: true,

      distDir: './dist',
      targetDir: '../nonebot_plugin_gocqhttp/web/dist',

      afterBuild(configs) {
        copyFolderRecursively(
          configs.quasarConf.build.distDir,
          // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
          configs.quasarConf.build.targetDir
        );
      },

      // https://quasar.dev/quasar-cli/handling-webpack
      // "chain" is a webpack-chain object https://github.com/neutrinojs/webpack-chain
      chainWebpack(chain) {
        chain
          .plugin('monaco-editor-webpack-plugin')
          .use(MonacoWebpackPlugin, [
            {
              languages: ['yaml', 'json'],
              filename: '[name].worker.[contenthash].js',
              features: [
                '!accessibilityHelp',
                '!browser',
                '!clipboard',
                '!contextmenu',
                '!colorPicker',
                '!find',
                '!folding',
                '!gotoError',
                '!gotoLine',
                '!inPlaceReplace',
                '!links',
                '!parameterHints',
                '!quickCommand',
                '!quickOutline',
                '!referenceSearch',
                '!rename',
                '!smartSelect',
                '!toggleHighContrast',
                '!toggleTabFocusMode',
                '!transpose',
              ],
            },
          ])
          .end()
          .optimization.splitChunks({
            chunks: 'all',
            maxSize: 512 * 1024,
            minSize: 256 * 1024,
          })
          .set('chunkIds', 'deterministic')
          .end();
      },
    },

    // Full list of options: https://quasar.dev/quasar-cli/quasar-conf-js#Property%3A-devServer
    devServer: {
      server: {
        type: 'http',
      },
      port: 8080,
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:3000/go-cqhttp',
          changeOrigin: true,
          ws: true,
        },
      },
      open: false,
    },

    // https://quasar.dev/quasar-cli/quasar-conf-js#Property%3A-framework
    framework: {
      config: {},

      // iconSet: 'material-icons', // Quasar icon set
      lang: 'zh-CN', // Quasar language pack

      // For special cases outside of where the auto-import strategy can have an impact
      // (like functional components as one of the examples),
      // you can manually specify Quasar components/directives to be available everywhere:
      //
      // components: [],
      // directives: [],

      // Quasar plugins
      plugins: ['Loading', 'LoadingBar', 'Notify', 'Dialog', 'Dark'],
    },

    // animations: 'all', // --- includes all animations
    // https://quasar.dev/options/animations
    animations: ['fadeIn', 'fadeOut'],

    // https://quasar.dev/quasar-cli/developing-ssr/configuring-ssr
    ssr: {
      pwa: false,

      // manualStoreHydration: true,
      // manualPostHydrationTrigger: true,

      prodPort: 3000, // The default port that the production server should use
      // (gets superseded if process.env.PORT is specified at runtime)

      maxAge: 1000 * 60 * 60 * 24 * 30,
      // Tell browser when a file from the server should expire from cache (in ms)

      chainWebpackWebserver(/* chain */) {
        //
      },

      middlewares: [
        ctx.prod ? 'compression' : '',
        'render', // keep this as last one
      ],
    },

    // https://quasar.dev/quasar-cli/developing-pwa/configuring-pwa
    pwa: {
      workboxPluginMode: 'GenerateSW', // 'GenerateSW' or 'InjectManifest'
      workboxOptions: {}, // only for GenerateSW

      // for the custom service worker ONLY (/src-pwa/custom-service-worker.[js|ts])
      // if using workbox in InjectManifest mode
      chainWebpackCustomSW(/* chain */) {
        //
      },

      manifest: {
        name: 'NoneBot Plugin Go-CQHTTP',
        short_name: 'NoneBot Plugin Go-CQHTTP',
        description:
          'A plugin to run go-cqhttp directly in NoneBot2, without additional download and installation.',
        display: 'standalone',
        orientation: 'portrait',
        background_color: '#ffffff',
        theme_color: '#027be3',
        icons: [
          {
            src: 'icons/icon-128x128.png',
            sizes: '128x128',
            type: 'image/png',
          },
          {
            src: 'icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'icons/icon-256x256.png',
            sizes: '256x256',
            type: 'image/png',
          },
          {
            src: 'icons/icon-384x384.png',
            sizes: '384x384',
            type: 'image/png',
          },
          {
            src: 'icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    },

    // Full list of options: https://quasar.dev/quasar-cli/developing-cordova-apps/configuring-cordova
    cordova: {
      // noIosLegacyBuildFlag: true, // uncomment only if you know what you are doing
    },

    // Full list of options: https://quasar.dev/quasar-cli/developing-capacitor-apps/configuring-capacitor
    capacitor: {
      hideSplashscreen: true,
    },

    // Full list of options: https://quasar.dev/quasar-cli/developing-electron-apps/configuring-electron
    electron: {
      bundler: 'packager', // 'packager' or 'builder'

      packager: {
        // https://github.com/electron-userland/electron-packager/blob/master/docs/api.md#options
        // OS X / Mac App Store
        // appBundleId: '',
        // appCategoryType: '',
        // osxSign: '',
        // protocol: 'myapp://path',
        // Windows only
        // win32metadata: { ... }
      },

      builder: {
        // https://www.electron.build/configuration/configuration

        appId: 'nonebot-plugin-gocqhttp-frontend',
      },

      // "chain" is a webpack-chain object https://github.com/neutrinojs/webpack-chain
      chainWebpack(/* chain */) {
        // do something with the Electron main process Webpack cfg
        // extendWebpackMain also available besides this chainWebpackMain
      },

      // "chain" is a webpack-chain object https://github.com/neutrinojs/webpack-chain
      chainWebpackPreload(/* chain */) {
        // do something with the Electron main process Webpack cfg
        // extendWebpackPreload also available besides this chainWebpackPreload
      },
    },
  };
});
