const { defineConfig } = require('@vue/cli-service')
const TerserPlugin = require('terser-webpack-plugin')

module.exports = defineConfig({
  transpileDependencies: true,

  // 生产环境优化
  productionSourceMap: false, // 关闭 source map，减小体积

  // 构建输出目录
  outputDir: 'dist',

  // 静态资源目录
  assetsDir: 'static',

  // 代码分割和优化配置
  configureWebpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          // 第三方库单独打包
          vendor: {
            name: 'chunk-vendors',
            test: /[\\/]node_modules[\\/]/,
            priority: 10,
            chunks: 'initial',
            reuseExistingChunk: true
          },
          // View UI Plus 单独打包
          viewUI: {
            name: 'chunk-viewui',
            test: /[\\/]node_modules[\\/](view-ui-plus|iview)[\\/]/,
            priority: 20,
            chunks: 'all',
            reuseExistingChunk: true
          },
          // ECharts 单独打包
          echarts: {
            name: 'chunk-echarts',
            test: /[\\/]node_modules[\\/](echarts|vue-echarts)[\\/]/,
            priority: 20,
            chunks: 'all',
            reuseExistingChunk: true
          },
          // Axios 单独打包
          axios: {
            name: 'chunk-axios',
            test: /[\\/]node_modules[\\/]axios[\\/]/,
            priority: 20,
            chunks: 'all',
            reuseExistingChunk: true
          },
          // 公共代码
          common: {
            name: 'chunk-common',
            minChunks: 2,
            priority: 5,
            chunks: 'initial',
            reuseExistingChunk: true
          }
        }
      },
      // 生产环境移除 console.log
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              // 移除 console
              drop_console: true,
              drop_debugger: true,
              // 纯粹功能优化
              pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn'],
            },
          },
        }),
      ],
    }
  },

  // 文件名哈希（浏览器缓存）
  chainWebpack: config => {
    // 生产环境配置
    if (process.env.NODE_ENV === 'production') {
      // 文件名添加 contenthash
      config.output.filename('js/[name].[contenthash:8].js')
      config.output.chunkFilename('js/[name].[contenthash:8].js')

      // CSS 文件名添加 contenthash
      config.plugin('extract-css').tap(args => [{
        filename: 'css/[name].[contenthash:8].css',
        chunkFilename: 'css/[name].[contenthash:8].css'
      }])

      // 图片优化
      config.module
        .rule('images')
        .test(/\.(png|jpe?g|gif|webp)(\?.*)?$/)
        .use('image-webpack-loader')
        .loader('image-webpack-loader')
        .options({
          mozjpeg: { progressive: true, quality: 65 },
          optipng: { enabled: false },
          pngquant: { quality: [0.65, 0.90], speed: 4 },
          gifsicle: { interlaced: false },
        })
    }
  },

  // 开发服务器配置
  devServer: {
    port: 8080,
    host: '0.0.0.0',
    open: false,
    hot: true,
    client: {
      overlay: {
        errors: true,
        warnings: false
      }
    },
    proxy: {
      '/api': {
        // VUE_APP_BACKEND_URL 在 Docker 内由 docker-compose 注入为 http://backend:8000
        // 本地开发不设置该变量时，回落到 localhost:8000
        target: process.env.VUE_APP_BACKEND_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,
        secure: false
      }
    }
  },

  // PWA 配置（可选）
  pwa: {
    name: '在线考试系统',
    themeColor: '#1890ff',
    backgroundColor: '#ffffff',
    display: 'standalone',
    // 图标配置
    iconPaths: {
      favicon32: 'img/icons/favicon-32x32.png',
      favicon16: 'img/icons/favicon-16x16.png',
      appleTouchIcon: 'img/icons/apple-touch-icon-180x180.png',
      maskIcon: 'img/icons/safari-pinned-tab.svg',
      msTileImage: 'img/icons/mstile-150x150.png'
    }
  },

  // CSS 提取和优化
  css: {
    extract: {
      filename: 'css/[name].[contenthash:8].css',
      chunkFilename: 'css/[name].[contenthash:8].css'
    },
    sourceMap: false
  },

  // 并行构建
  parallel: require('os').cpus().length > 1
})
