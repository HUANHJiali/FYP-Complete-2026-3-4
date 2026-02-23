import axios from 'axios'
import qs from 'qs'

import { Notice } from "view-ui-plus";

// 从环境变量获取API地址，如果没有则使用默认值
const getBaseURL = () => {
	// 使用代理，让vue.config.js处理
	return '/api'
}

const service = axios.create({
	baseURL: getBaseURL(),
	timeout: 30000,
	withCredentials: false
})

service.interceptors.request.use(config => {
	
    if(config.method === "post"){
        const isFormData = (typeof FormData !== 'undefined') && (config.data instanceof FormData);
        if(!isFormData){
            const isJson = (config.headers && String(config.headers['Content-Type']).includes('application/json'))
            if (!isJson){
                config.data = qs.stringify(config.data,  { indices: false });
            }
        }
    }
	
	return config;
}, error => {
	Promise.reject(error)
})

// respone拦截器
service.interceptors.response.use(
    success => {
        if (typeof success.data === 'string' || success.request?.responseType === 'blob'){
            return success;
        }

        if (success.data.code == 0) {
            return success.data;
        }else if (success.data.code == 1){
            return success.data;
        } else {
            const url = success?.config?.url || '';
            if (url.includes('/exit/')) {
                return { code: 0, msg: '退出成功', data: {} };
            }
            Notice.error({
                duration: 3,
                title: success.data.msg
            });
            return Promise.reject(success.data);
		}
	},
	error => {
        const url = error?.config?.url || '';
        if (url.includes('/exit/')) {
            return Promise.resolve({ code: 0, msg: '退出成功', data: {} });
        }
        
        let errorMessage = '系统异常，请求中断';
        
        if (error.code === 'ECONNABORTED') {
            errorMessage = '请求超时，请检查网络连接或稍后重试';
        } else if (error.message === 'Network Error') {
            errorMessage = '网络连接失败，请检查后端服务是否已启动';
        } else if (error.response) {
            const status = error.response.status;
            if (status === 404) {
                errorMessage = '请求的接口不存在（404）';
            } else if (status === 500) {
                errorMessage = '服务器内部错误（500）';
            } else if (status === 403) {
                errorMessage = '访问被拒绝（403）';
            } else {
                errorMessage = `服务器错误（${status}）`;
            }
        } else if (error.request) {
            errorMessage = '无法连接到服务器';
        }
        
        console.error('API请求错误:', error);
        
        Notice.error({
            duration: 5,
            title: errorMessage
        });
        
        return Promise.reject(error);
	}
)

export default service
