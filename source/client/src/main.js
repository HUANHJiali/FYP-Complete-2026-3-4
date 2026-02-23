import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import ViewUI from 'view-ui-plus';
import 'view-ui-plus/dist/styles/viewuiplus.css';
import './assets/style.css';
import './assets/animations.css';
import './assets/design-system.css';
import './assets/theme-enhanced.css';

// ECharts主题配置
import * as echarts from 'echarts/core';

// 深色主题配置
const darkTheme = {
    backgroundColor: 'transparent',
    textStyle: {
        color: '#fff'
    },
    title: {
        textStyle: {
            color: '#fff'
        }
    },
    legend: {
        textStyle: {
            color: '#fff'
        }
    },
    xAxis: {
        axisLine: {
            lineStyle: {
                color: '#666'
            }
        },
        axisLabel: {
            color: '#fff'
        }
    },
    yAxis: {
        axisLine: {
            lineStyle: {
                color: '#666'
            }
        },
        axisLabel: {
            color: '#fff'
        }
    }
};

// 注册深色主题
echarts.registerTheme('dark', darkTheme);

import initMenu from "./utils/menus.js";

router.beforeEach((to,from,next)=>{

  if(to.path == '/'){
    next();
  }else{
    if(store.state.menus != null){

        next();
    }else{

      initMenu(router, store);
      next();
    }
  }
});

const app = createApp(App);
app.use(store);
app.use(router);
app.use(ViewUI);

app.mount('#app');
