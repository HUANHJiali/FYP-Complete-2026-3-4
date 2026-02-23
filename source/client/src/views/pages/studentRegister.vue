<template>
    <div class="fater-body-show">
        <div class="page-header animate-fade-in-up">
            <div class="header-content">
                <Icon type="ios-person-add" class="header-icon" />
                <div class="header-text">
                    <h2>学生注册</h2>
                    <p>创建新的学生账户</p>
                </div>
            </div>
        </div>

        <Card class="register-card animate-fade-in-up delay-100">
            <template #title>
                <div class="card-title">
                    <Icon type="ios-create" class="title-icon" />
                    <span>学生信息注册</span>
                </div>
            </template>
            
            <Form ref="registerForm" :model="registerForm" :rules="rules" :label-width="100" class="register-form">
                <Row :gutter="20">
                    <Col span="12">
                        <FormItem label="年级" prop="gradeId">
                            <Select 
                                v-model="registerForm.gradeId" 
                                placeholder="请选择年级"
                                class="modern-select" transfer>
                                <Option v-for="grade in grades" 
                                    :key="grade.id" 
                                    :value="grade.id">{{ grade.name }}</Option>
                            </Select>
                        </FormItem>
                    </Col>
                    <Col span="12">
                        <FormItem label="学院" prop="collegeId">
                            <Select 
                                v-model="registerForm.collegeId" 
                                placeholder="请选择学院"
                                class="modern-select" transfer>
                                <Option v-for="college in colleges" 
                                    :key="college.id" 
                                    :value="college.id">{{ college.name }}</Option>
                            </Select>
                        </FormItem>
                    </Col>
                </Row>

                <Row :gutter="20">
                    <Col span="12">
                        <FormItem label="用户名" prop="userName">
                            <Input 
                                v-model="registerForm.userName" 
                                placeholder="请输入用户名"
                                class="modern-input"
                                prefix="ios-person">
                            </Input>
                        </FormItem>
                    </Col>
                    <Col span="12">
                        <FormItem label="密码" prop="passWord">
                            <Input 
                                type="password" 
                                v-model="registerForm.passWord" 
                                placeholder="请输入密码"
                                class="modern-input"
                                prefix="ios-lock">
                            </Input>
                        </FormItem>
                    </Col>
                </Row>

                <Row :gutter="20">
                    <Col span="12">
                        <FormItem label="确认密码" prop="confirmPassword">
                            <Input 
                                type="password" 
                                v-model="registerForm.confirmPassword" 
                                placeholder="请确认密码"
                                class="modern-input"
                                prefix="ios-lock">
                            </Input>
                        </FormItem>
                    </Col>
                    <Col span="12">
                        <FormItem label="真实姓名" prop="name">
                            <Input 
                                v-model="registerForm.name" 
                                placeholder="请输入真实姓名"
                                class="modern-input"
                                prefix="ios-person">
                            </Input>
                        </FormItem>
                    </Col>
                </Row>

                <Row :gutter="20">
                    <Col span="12">
                        <FormItem label="性别" prop="gender">
                            <RadioGroup v-model="registerForm.gender" class="gender-group">
                                <Radio label="男">男</Radio>
                                <Radio label="女">女</Radio>
                            </RadioGroup>
                        </FormItem>
                    </Col>
                    <Col span="12">
                        <FormItem label="年龄" prop="age">
                            <InputNumber 
                                v-model="registerForm.age" 
                                :min="1" 
                                :max="100"
                                placeholder="请输入年龄"
                                class="modern-input-number">
                            </InputNumber>
                        </FormItem>
                    </Col>
                </Row>

                <FormItem>
                    <Button 
                        type="primary" 
                        @click="submitForm('registerForm')"
                        class="submit-btn btn-ripple"
                        :loading="submitting">
                        <Icon type="ios-checkmark" />
                        注册账户
                    </Button>
                    <Button 
                        @click="resetForm('registerForm')"
                        class="reset-btn btn-ripple">
                        <Icon type="ios-refresh" />
                        重置表单
                    </Button>
                </FormItem>
            </Form>
        </Card>
    </div>
</template>

<style scoped>
.page-header {
    margin-bottom: 24px;
    padding: 30px;
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border-radius: 15px;
    color: white;
    box-shadow: 0 10px 30px rgba(24, 144, 255, 0.3);
}

.header-content {
    display: flex;
    align-items: center;
    gap: 16px;
}

.header-icon {
    font-size: 36px;
    color: rgba(255, 255, 255, 0.9);
}

.header-text h2 {
    margin: 0 0 8px 0;
    font-size: 28px;
    font-weight: 600;
    color: #fff;
}

.header-text p {
    margin: 0;
    opacity: 0.9;
    font-size: 16px;
    color: rgba(255, 255, 255, 0.9);
}

.register-card {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(24, 144, 255, 0.1);
    border: 1px solid rgba(24, 144, 255, 0.1);
    background: #fff;
    transition: all 0.3s ease;
}

.register-card:hover {
    box-shadow: 0 8px 30px rgba(24, 144, 255, 0.15);
}

.card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
    color: #262626;
}

.title-icon {
    color: #1890ff;
}

.register-form {
    padding: 20px 0;
}

.modern-select,
.modern-input,
.modern-input-number {
    width: 100%;
    border-radius: 8px;
    border: 1px solid rgba(24, 144, 255, 0.2);
    transition: all 0.3s ease;
}

.modern-select:focus,
.modern-input:focus,
.modern-input-number:focus {
    border-color: #1890ff;
    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.gender-group {
    display: flex;
    gap: 20px;
}

.gender-group .ivu-radio-wrapper {
    padding: 8px 16px;
    border: 1px solid rgba(24, 144, 255, 0.2);
    border-radius: 8px;
    transition: all 0.3s ease;
}

.gender-group .ivu-radio-wrapper:hover {
    border-color: #1890ff;
    background: rgba(24, 144, 255, 0.05);
}

.gender-group .ivu-radio-wrapper-checked {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border-color: #1890ff;
    color: #fff;
}

.submit-btn,
.reset-btn {
    margin-right: 12px;
    height: 40px;
    padding: 0 24px;
    border-radius: 8px;
}

.submit-btn {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
    color: #fff;
    transition: all 0.3s ease;
}

.submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
}

.reset-btn {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    color: #6c757d;
    transition: all 0.3s ease;
}

.reset-btn:hover {
    background: #e9ecef;
    transform: translateY(-2px);
}

.btn-ripple {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.btn-ripple:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(24, 144, 255, 0.3);
}

.animate-fade-in-up {
    animation: fadeInUp 0.6s ease-out;
}

.animate-fade-in-up.delay-100 {
    animation-delay: 0.1s;
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

/* 响应式设计 */
@media (max-width: 768px) {
    .page-header {
        padding: 20px;
    }

    .header-text h2 {
        font-size: 22px;
    }

    .gender-group {
        flex-direction: column;
        gap: 12px;
    }
}
</style>

<script>
import { getAllGrades, getAllColleges, studentRegister } from '../../api/index.js';

export default {
    name: 'StudentRegister',
    data() {
        const validateConfirmPassword = (rule, value, callback) => {
            if (value !== this.registerForm.passWord) {
                callback(new Error('两次输入的密码不一致'));
            } else {
                callback();
            }
        };

        return {
            grades: [],
            colleges: [],
            submitting: false,
            registerForm: {
                gradeId: '',
                collegeId: '',
                userName: '',
                passWord: '',
                confirmPassword: '',
                name: '',
                gender: '男',
                age: 18
            },
            rules: {
                gradeId: [
                    { required: true, message: '请选择年级', trigger: 'change' }
                ],
                collegeId: [
                    { required: true, message: '请选择学院', trigger: 'change' }
                ],
                userName: [
                    { required: true, message: '请输入用户名', trigger: 'blur' },
                    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
                ],
                passWord: [
                    { required: true, message: '请输入密码', trigger: 'blur' },
                    { min: 6, max: 20, message: '密码长度在6到20个字符', trigger: 'blur' }
                ],
                confirmPassword: [
                    { required: true, message: '请确认密码', trigger: 'blur' },
                    { validator: validateConfirmPassword, trigger: 'blur' }
                ],
                name: [
                    { required: true, message: '请输入真实姓名', trigger: 'blur' }
                ],
                gender: [
                    { required: true, message: '请选择性别', trigger: 'change' }
                ],
                age: [
                    { required: true, message: '请输入年龄', trigger: 'blur' },
                    { type: 'number', min: 1, max: 100, message: '年龄必须在1-100之间', trigger: 'blur' }
                ]
            }
        };
    },
    methods: {
        submitForm(formName) {
            this.$refs[formName].validate((valid) => {
                if (valid) {
                    this.submitting = true;
                    
                    // 生成学生ID (格式: S + 年月日 + 4位序号)
                    const now = new Date();
                    const dateStr = now.getFullYear().toString() + 
                                  (now.getMonth() + 1).toString().padStart(2, '0') + 
                                  now.getDate().toString().padStart(2, '0');
                    const studentId = 'S' + dateStr + '00001'; // 简化处理，实际应该查询database获取下一个序号
                    
                    // 准备注册数据
                    const registerData = {
                        id: studentId,
                        userName: this.registerForm.userName,
                        passWord: this.registerForm.passWord,
                        name: this.registerForm.name,
                        gender: this.registerForm.gender,
                        age: this.registerForm.age,
                        gradeId: this.registerForm.gradeId,
                        collegeId: this.registerForm.collegeId
                    };
                    
                    // 调用注册API
                    studentRegister(registerData).then(resp => {
                        if (resp.code === 0) {
                            this.$Message.success('注册成功！');
                            this.resetForm(formName);
                            // 注册成功后跳转到登录页面
                            this.$router.push('/login');
                        } else {
                            this.$Message.error(resp.msg || '注册失败，请重试');
                        }
                    }).catch(error => {
                        console.error('注册失败:', error);
                        this.$Message.error('注册失败，请检查网络连接');
                    }).finally(() => {
                        this.submitting = false;
                    });
                } else {
                    this.$Message.error('请检查表单信息');
                }
            });
        },
        resetForm(formName) {
            this.$refs[formName].resetFields();
        },
        loadGrades() {
            getAllGrades().then(resp => {
                this.grades = resp.data;
            });
        },
        loadColleges() {
            getAllColleges().then(resp => {
                this.colleges = resp.data;
            });
        }
    },
    mounted() {
        this.loadGrades();
        this.loadColleges();
    }
};
</script>
