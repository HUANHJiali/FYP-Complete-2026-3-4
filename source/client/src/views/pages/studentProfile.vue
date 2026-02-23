<template>
    <div class="fater-body-show">
        <div class="page-header animate-fade-in-up">
            <div class="header-content">
                <Icon type="ios-person" class="header-icon" />
                <div class="header-text">
                    <h2>个人信息</h2>
                    <p>管理您的个人资料和账户信息</p>
                </div>
            </div>
        </div>

        <Row :gutter="24" class="profile-container">
            <!-- 左侧个人信息卡片 -->
            <Col span="8">
                <Card class="profile-card animate-fade-in-up delay-100">
                    <div class="avatar-section">
                        <div class="avatar-container">
                            <img 
                                :src="userInfo.avatar || '/default-avatar.png'" 
                                alt="头像" 
                                class="avatar-image"
                                @error="handleAvatarError">
                            <div class="avatar-overlay">
                                <Icon type="ios-camera" class="camera-icon" />
                            </div>
                            <input 
                                type="file" 
                                ref="avatarInput" 
                                accept="image/*" 
                                @change="handleAvatarChange"
                                class="avatar-input">
                        </div>
                        <Button 
                            type="primary" 
                            @click="triggerAvatarUpload"
                            class="upload-btn btn-ripple">
                            <Icon type="ios-camera" />
                            更换头像
                        </Button>
                    </div>
                    
                    <div class="user-info">
                        <h3 class="user-name">{{ userInfo.name }}</h3>
                        <p class="user-id">学号：{{ userInfo.id }}</p>
                        <p class="user-role">学生</p>
                    </div>
                    
                    <div class="quick-stats">
                        <div class="stat-item">
                            <div class="stat-number">{{ examCount }}</div>
                            <div class="stat-label">参加考试</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{{ avgScore }}</div>
                            <div class="stat-label">平均分</div>
                        </div>
                    </div>
                </Card>
            </Col>

            <!-- 右侧信息编辑区域 -->
            <Col span="16">
                <Card class="edit-card animate-fade-in-up delay-200">
                    <template #title>
                        <div class="card-title">
                            <Icon type="ios-create" class="title-icon" />
                            <span>编辑个人信息</span>
                        </div>
                    </template>
                    
                    <Form 
                        ref="profileForm" 
                        :model="profileForm" 
                        :rules="rules" 
                        :label-width="100" 
                        class="profile-form">
                        
                        <Row :gutter="20">
                            <Col span="12">
                                <FormItem label="真实姓名" prop="name">
                                    <Input 
                                        v-model="profileForm.name" 
                                        placeholder="请输入真实姓名"
                                        class="modern-input"
                                        prefix="ios-person">
                                    </Input>
                                </FormItem>
                            </Col>
                            <Col span="12">
                                <FormItem label="用户名" prop="userName">
                                    <Input 
                                        v-model="profileForm.userName" 
                                        placeholder="请输入用户名"
                                        class="modern-input"
                                        prefix="ios-person">
                                    </Input>
                                </FormItem>
                            </Col>
                        </Row>

                        <Row :gutter="20">
                            <Col span="12">
                                <FormItem label="性别" prop="gender">
                                    <RadioGroup v-model="profileForm.gender" class="gender-group">
                                        <Radio label="男">男</Radio>
                                        <Radio label="女">女</Radio>
                                    </RadioGroup>
                                </FormItem>
                            </Col>
                            <Col span="12">
                                <FormItem label="年龄" prop="age">
                                    <InputNumber 
                                        v-model="profileForm.age" 
                                        :min="1" 
                                        :max="100"
                                        placeholder="请输入年龄"
                                        class="modern-input-number">
                                    </InputNumber>
                                </FormItem>
                            </Col>
                        </Row>

                        <Row :gutter="20">
                            <Col span="12">
                                <FormItem label="手机号码" prop="phone">
                                    <Input 
                                        v-model="profileForm.phone" 
                                        placeholder="请输入手机号码"
                                        class="modern-input"
                                        prefix="ios-call">
                                    </Input>
                                </FormItem>
                            </Col>
                            <Col span="12">
                                <FormItem label="邮箱地址" prop="email">
                                    <Input 
                                        v-model="profileForm.email" 
                                        placeholder="请输入邮箱地址"
                                        class="modern-input"
                                        prefix="ios-mail">
                                    </Input>
                                </FormItem>
                            </Col>
                        </Row>

                        <Row :gutter="20">
                            <Col span="12">
                                <FormItem label="所属学院" prop="collegeName">
                                    <Input 
                                        v-model="profileForm.collegeName" 
                                        placeholder="所属学院"
                                        class="modern-input"
                                        prefix="ios-ribbon"
                                        disabled>
                                    </Input>
                                </FormItem>
                            </Col>
                            <Col span="12">
                                <FormItem label="所在班级" prop="gradeName">
                                    <Input 
                                        v-model="profileForm.gradeName" 
                                        placeholder="所在班级"
                                        class="modern-input"
                                        prefix="ios-people"
                                        disabled>
                                    </Input>
                                </FormItem>
                            </Col>
                        </Row>

                        <FormItem label="个人简介" prop="bio">
                            <Input 
                                type="textarea" 
                                v-model="profileForm.bio" 
                                placeholder="请输入个人简介..."
                                :rows="4"
                                class="modern-textarea">
                            </Input>
                        </FormItem>

                        <FormItem>
                            <Button 
                                type="primary" 
                                @click="saveProfile()"
                                class="save-btn btn-ripple"
                                :loading="saving">
                                <Icon type="ios-checkmark" />
                                保存修改
                            </Button>
                            <Button 
                                @click="resetForm()"
                                class="reset-btn btn-ripple">
                                <Icon type="ios-refresh" />
                                重置
                            </Button>
                        </FormItem>
                    </Form>
                </Card>

                <!-- 密码修改卡片 -->
                <Card class="password-card animate-fade-in-up delay-300">
                    <template #title>
                        <div class="card-title">
                            <Icon type="ios-lock" class="title-icon" />
                            <span>修改密码</span>
                        </div>
                    </template>
                    
                    <Form 
                        ref="passwordForm" 
                        :model="passwordForm" 
                        :rules="passwordRules" 
                        :label-width="100" 
                        class="password-form">
                        
                        <FormItem label="当前密码" prop="currentPassword">
                            <Input 
                                type="password" 
                                v-model="passwordForm.currentPassword" 
                                placeholder="请输入当前密码"
                                class="modern-input"
                                prefix="ios-lock">
                            </Input>
                        </FormItem>

                        <FormItem label="新密码" prop="newPassword">
                            <Input 
                                type="password" 
                                v-model="passwordForm.newPassword" 
                                placeholder="请输入新密码"
                                class="modern-input"
                                prefix="ios-lock">
                            </Input>
                        </FormItem>

                        <FormItem label="确认密码" prop="confirmPassword">
                            <Input 
                                type="password" 
                                v-model="passwordForm.confirmPassword" 
                                placeholder="请确认新密码"
                                class="modern-input"
                                prefix="ios-lock">
                            </Input>
                        </FormItem>

                        <FormItem>
                            <Button 
                                type="warning" 
                                @click="changePassword()"
                                class="change-btn btn-ripple"
                                :loading="changingPassword">
                                <Icon type="ios-lock" />
                                修改密码
                            </Button>
                        </FormItem>
                    </Form>
                </Card>
            </Col>
        </Row>

        <!-- 成绩进步曲线 -->
        <Row :gutter="24" class="mt-24">
            <Col span="24">
                <Card class="progress-chart-card animate-fade-in-up delay-400">
                    <template #title>
                        <div class="card-title">
                            <Icon type="ios-trending-up" class="title-icon" />
                            <span>成绩进步曲线</span>
                        </div>
                    </template>
                    <ProgressChart :studentId="userInfo.id" />
                </Card>
            </Col>
        </Row>
    </div>
</template>

<style scoped>
.page-header {
    margin-bottom: 24px;
    padding: 24px;
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
    border-radius: 12px;
    color: white;
}

.header-content {
    display: flex;
    align-items: center;
    gap: 16px;
}

.header-icon {
    font-size: 32px;
    color: rgba(255, 255, 255, 0.9);
}

.header-text h2 {
    margin: 0 0 8px 0;
    font-size: 28px;
    font-weight: 600;
}

.header-text p {
    margin: 0;
    opacity: 0.9;
    font-size: 16px;
}

.profile-container {
    margin-bottom: 24px;
}

.profile-card {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    text-align: center;
    padding: 24px;
}

.avatar-section {
    margin-bottom: 24px;
}

.avatar-container {
    position: relative;
    width: 120px;
    height: 120px;
    margin: 0 auto 16px;
    border-radius: 50%;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s ease;
}

.avatar-container:hover .avatar-overlay {
    opacity: 1;
}

.avatar-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.avatar-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.camera-icon {
    color: white;
    font-size: 24px;
}

.avatar-input {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
}

.upload-btn {
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
    border: none;
    height: 36px;
    padding: 0 20px;
    border-radius: 8px;
}

.user-info {
    margin-bottom: 24px;
}

.user-name {
    font-size: 24px;
    font-weight: 600;
    color: #262626;
    margin: 0 0 8px 0;
}

.user-id {
    color: #8c8c8c;
    margin: 0 0 4px 0;
    font-size: 14px;
}

.user-role {
    color: #1890ff;
    margin: 0;
    font-weight: 500;
    font-size: 14px;
}

.quick-stats {
    display: flex;
    gap: 20px;
    justify-content: center;
}

.stat-item {
    text-align: center;
}

.stat-number {
    font-size: 24px;
    font-weight: 700;
    color: #1890ff;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 12px;
    color: #8c8c8c;
}

.edit-card,
.password-card {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    margin-bottom: 24px;
}

.card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
}

.title-icon {
    color: #1890ff;
}

.profile-form,
.password-form {
    padding: 20px 0;
}

.modern-input,
.modern-input-number,
.modern-textarea {
    width: 100%;
}

.gender-group {
    display: flex;
    gap: 20px;
}

.save-btn,
.reset-btn,
.change-btn {
    height: 40px;
    padding: 0 24px;
    border-radius: 8px;
    margin-right: 12px;
}

.save-btn {
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
    border: none;
}

.reset-btn {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    color: #6c757d;
}

.change-btn {
    background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
    border: none;
}

.btn-ripple {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.btn-ripple:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.animate-fade-in-up {
    animation: fadeInUp 0.6s ease-out;
}

.animate-fade-in-up.delay-100 {
    animation-delay: 0.1s;
}

.animate-fade-in-up.delay-200 {
    animation-delay: 0.2s;
}

.animate-fade-in-up.delay-300 {
    animation-delay: 0.3s;
}

.animate-fade-in-up.delay-400 {
    animation-delay: 0.4s;
}

.mt-24 {
    margin-top: 24px;
}

.progress-chart-card {
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>

<script>
import { getLoginUser, updSessionInfo, updSessionPwd } from '@/api/index.js'
import ProgressChart from '@/components/ProgressChart.vue'

export default {
    name: 'StudentProfile',
    components: {
        ProgressChart
    },
    data() {
        const validateConfirmPassword = (rule, value, callback) => {
            if (value !== this.passwordForm.newPassword) {
                callback(new Error('两次输入的密码不一致'));
            } else {
                callback();
            }
        };

        return {
            userInfo: {},
            saving: false,
            changingPassword: false,
            profileForm: {
                name: '',
                userName: '',
                gender: '男',
                age: 18,
                phone: '',
                email: '',
                collegeName: '',
                gradeName: '',
                bio: ''
            },
            passwordForm: {
                currentPassword: '',
                newPassword: '',
                confirmPassword: ''
            },
            rules: {
                name: [
                    { required: true, message: '请输入真实姓名', trigger: 'blur' }
                ],
                userName: [
                    { required: true, message: '请输入用户名', trigger: 'blur' },
                    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
                ],
                phone: [
                    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
                ],
                email: [
                    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
                ],
                age: [
                    { required: true, message: '请输入年龄', trigger: 'blur' },
                    { type: 'number', min: 1, max: 100, message: '年龄必须在1-100之间', trigger: 'blur' }
                ]
            },
            passwordRules: {
                currentPassword: [
                    { required: true, message: '请输入当前密码', trigger: 'blur' }
                ],
                newPassword: [
                    { required: true, message: '请输入新密码', trigger: 'blur' },
                    { min: 6, max: 20, message: '密码长度在6到20个字符', trigger: 'blur' }
                ],
                confirmPassword: [
                    { required: true, message: '请确认新密码', trigger: 'blur' },
                    { validator: validateConfirmPassword, trigger: 'blur' }
                ]
            }
        };
    },
    computed: {
        examCount() {
            // 这里可以从store或API获取真实的考试次数
            return this.userInfo.examCount || 0;
        },
        avgScore() {
            // 这里可以从store或API获取真实的平均分
            return this.userInfo.avgScore || 0;
        }
    },
    methods: {
        async loadUserInfo() {
            try {
                const token = this.$store.state.token || sessionStorage.getItem('token');
                if (!token) {
                    this.$Message.error('请先登录');
                    return;
                }

                const resp = await getLoginUser(token);
                if (resp.code === 0) {
                    this.userInfo = resp.data;
                    this.profileForm = {
                        name: resp.data.name || '',
                        userName: resp.data.userName || '',
                        gender: resp.data.gender || '男',
                        age: resp.data.age || 18,
                        phone: resp.data.phone || '',
                        email: resp.data.email || '',
                        collegeName: resp.data.collegeName || '',
                        gradeName: resp.data.gradeName || '',
                        bio: resp.data.bio || ''
                    };
                } else {
                    this.$Message.error(resp.msg || '获取用户信息失败');
                }
            } catch (error) {
                console.error('获取用户信息失败:', error);
                this.$Message.error('获取用户信息失败');
            }
        },
        triggerAvatarUpload() {
            this.$refs.avatarInput.click();
        },
        handleAvatarChange(event) {
            const file = event.target.files[0];
            if (file) {
                // 文件大小验证
                if (file.size > 5 * 1024 * 1024) {
                    this.$Message.error('图片大小不能超过5MB');
                    return;
                }
                
                // 文件类型验证
                if (!file.type.startsWith('image/')) {
                    this.$Message.error('请选择图片文件');
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.userInfo.avatar = e.target.result;
                    this.$Message.success('头像上传成功');
                };
                reader.readAsDataURL(file);
                
                // 这里可以调用API上传头像到服务器
                // this.uploadAvatar(file);
            }
        },
        handleAvatarError() {
            this.userInfo.avatar = '/default-avatar.png';
        },
        async saveProfile() {
            this.$refs.profileForm.validate(async (valid) => {
                if (valid) {
                    try {
                        this.saving = true;
                        const token = this.$store.state.token || sessionStorage.getItem('token');
                        
                        const params = {
                            token: token,
                            userName: this.profileForm.userName,
                            name: this.profileForm.name,
                            gender: this.profileForm.gender,
                            age: this.profileForm.age
                        };
                        
                        const response = await updSessionInfo(params);
                        if (response.code === 0) {
                            this.$Message.success('个人信息更新成功');
                            // 重新加载用户信息
                            await this.loadUserInfo();
                        } else {
                            this.$Message.error(response.msg || '更新失败');
                        }
                    } catch (error) {
                        console.error('更新个人信息失败:', error);
                        this.$Message.error('更新个人信息失败');
                    } finally {
                        this.saving = false;
                    }
                } else {
                    this.$Message.error('请检查表单信息');
                }
            });
        },
        resetForm() {
            this.$refs.profileForm.resetFields();
            this.loadUserInfo();
        },
        async changePassword() {
            this.$refs.passwordForm.validate(async (valid) => {
                if (valid) {
                    try {
                        this.changingPassword = true;
                        const token = this.$store.state.token || sessionStorage.getItem('token');
                        
                        const params = {
                            token: token,
                            oldPwd: this.passwordForm.currentPassword,
                            newPwd: this.passwordForm.newPassword,
                            rePwd: this.passwordForm.confirmPassword
                        };
                        
                        const response = await updSessionPwd(params);
                        if (response.code === 0) {
                            this.$Message.success('密码修改成功');
                            this.$refs.passwordForm.resetFields();
                        } else {
                            this.$Message.error(response.msg || '密码修改失败');
                        }
                    } catch (error) {
                        console.error('修改密码失败:', error);
                        this.$Message.error('修改密码失败');
                    } finally {
                        this.changingPassword = false;
                    }
                } else {
                    this.$Message.error('请检查密码信息');
                }
            });
        }
    },
    mounted() {
        this.loadUserInfo();
    }
};
</script>
