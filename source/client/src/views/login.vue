<template>
    <div class="login-body">
        <div class="login-container">
            <div class="login-card">
                <div class="login-header">
                    <h2>在线考试管理系统</h2>
                    <p>欢迎使用智能考试平台</p>
                </div>
                <div class="login-form">
                    <Form ref="loginForm" :rules="rules" :model="loginForm" :label-width="0">
                        <FormItem prop="userName">
                            <Input
                                v-model="loginForm.userName"
                                placeholder="请输入学号或工号"
                                size="large"
                                prefix="ios-person"
                                class="login-input">
                            </Input>
                            <div class="input-tip">
                                <Icon type="ios-information-circle-outline" />
                                <span>请使用学号或工号登录（6-12位数字或字母）</span>
                            </div>
                        </FormItem>
                        <FormItem prop="passWord">
                            <Input
                                type="password"
                                v-model="loginForm.passWord"
                                placeholder="请输入您的密码"
                                size="large"
                                prefix="ios-lock"
                                class="login-input">
                            </Input>
                            <div class="input-tip">
                                <Icon type="ios-lock-outline" />
                                <span>请输入您设置的密码</span>
                            </div>
                        </FormItem>
                        <FormItem style="margin-top: 30px;">
                            <Button
                                style="width: 100%; height: 45px; font-size: 16px;"
                                @click="submitForm('loginForm')"
                                class="login-btn"
                                type="primary"
                                :loading="logging"
                                :disabled="logging">
                                {{ logging ? '登录中...' : '登录系统' }}
                            </Button>
                        </FormItem>
                    </Form>
                </div>
                <div class="login-footer">
                    <p>© 2024 在线考试管理系统 - 让学习更高效</p>
                </div>
            </div>
        </div>
    </div>
</template>

<style>
.login-body {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}

.login-body::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
    animation: bg-pulse 8s ease-in-out infinite;
    z-index: 1;
}

@keyframes bg-pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.5; }
}

.login-container {
    position: relative;
    z-index: 2;
    width: 100%;
    max-width: 420px;
    padding: 20px;
    animation: login-float 6s ease-in-out infinite;
}

@keyframes login-float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.login-card {
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 48px 40px;
    box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    position: relative;
    overflow: hidden;
}

.login-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: card-shine 3s ease-in-out infinite;
}

@keyframes card-shine {
    0% { left: -100%; }
    50%, 100% { left: 100%; }
}

.login-header {
    text-align: center;
    margin-bottom: 32px;
}

.login-header h2 {
    color: #0050b3;
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 12px;
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 1px;
}

.login-header p {
    color: #595959;
    font-size: 15px;
    margin: 0;
    font-weight: 500;
}

.login-form {
    margin-bottom: 20px;
}

.login-input {
    border-radius: 12px;
    border: 2px solid #e8e9ea;
    transition: all 0.3s ease;
    background: rgba(255, 255, 255, 0.9);
    font-size: 15px;
}

.login-input:hover {
    border-color: #40a9ff;
    transform: translateY(-1px);
}

.login-input:focus {
    border-color: #1890ff;
    box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.15);
    background: #fff;
    transform: translateY(-1px);
}

.login-btn {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
    border-radius: 12px;
    font-weight: 600;
    letter-spacing: 2px;
    transition: all 0.3s ease;
    box-shadow: 0 6px 20px rgba(24, 144, 255, 0.35);
}

.login-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(24, 144, 255, 0.5);
}

.login-btn:active {
    transform: translateY(-1px);
}

.login-footer {
    text-align: center;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.login-footer p {
    color: #999;
    font-size: 12px;
    margin: 0;
}

/* 输入提示 */
.input-tip {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
    padding: 0 4px;
    font-size: 12px;
    color: #8c8c8c;
}

.input-tip .ivu-icon {
    font-size: 14px;
    color: #1890ff;
}

/* 响应式设计 */
@media (max-width: 480px) {
    .login-container {
        padding: 12px;
        max-width: 100%;
    }
    
    .login-card {
        padding: 24px 16px;
        border-radius: 16px;
    }
    
    .login-header h2 {
        font-size: 22px;
        line-height: 1.2;
    }

    .login-header p {
        font-size: 13px;
    }

    .input-tip {
        font-size: 11px;
        line-height: 1.4;
    }

    .login-footer p {
        font-size: 11px;
    }

    .login-btn {
        letter-spacing: 1px;
    }
}
</style>

<script>
import initMenu from "../utils/menus.js";
import { login } from '../api/index.js';
export default {
    data() {

        return {
            loginForm: {
                userName: '',
                passWord: '',
            },
            logging: false,
            rules: {
                userName: [
                    { required: true, message: '请输入您的学号或工号', trigger: 'blur' },
                    { min: 3, max: 20, message: '账号长度应为3-20位', trigger: 'blur' }
                ],
                passWord: [
                    { required: true, message: '请输入您的密码', trigger: 'blur' }
                ],
            }
        }
    },
    methods: {
        submitForm (formName) {

            this.$refs[formName].validate((valid) => {
                if (valid) {
                    // 检查网络连接
                    if (!navigator.onLine) {
                        this.$Message.error('网络未连接，请检查网络设置');
                        return;
                    }

                    this.logging = true;

                    login(this.loginForm).then(res => {

                        if(res.code == 0){

                            this.$store.commit('setToken', res.data.token);
                            sessionStorage.setItem("token", res.data.token);
                            initMenu(this.$router, this.$store);
                            this.$Message.success('登录成功');
                            // 路由跳转由 initMenu 内部处理，此处不重复 push
                        }else{
                            // 根据错误码显示不同提示
                            if (res.code === 401) {
                                this.$Message.error('账号或密码错误，请重新输入');
                            } else if (res.code === 408) {
                                this.$Message.error('网络超时，请检查网络后重试');
                            } else {
                                this.$Message.warning(res.msg || '登录失败，请稍后重试');
                            }
                        }
                    }).catch(err => {
                        console.error('登录失败:', err);
                        // 网络错误或服务器错误
                        if (!navigator.onLine) {
                            this.$Message.error('网络未连接，请检查网络设置');
                        } else {
                            this.$Message.error('服务器繁忙，请稍后重试');
                        }
                    }).finally(() => {
                        this.logging = false;
                    });
                } else {

                    return false;
                }
            })
        }
    },
}
</script>
