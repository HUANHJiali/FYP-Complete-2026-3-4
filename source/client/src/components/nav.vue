<template>
	<Header class="fater-header-user">
		<Dropdown @on-click="handleUser" class="user-dropdown">
			<a href="javascript:void(0)" class="user-info">
				<Avatar icon="ios-person" size="small" class="user-avatar" />
				<span class="user-text">个人中心</span>
				<Icon type="ios-arrow-down" class="dropdown-icon"></Icon>
			</a>
			<template #list>
				<DropdownMenu class="user-dropdown-menu">
					<DropdownItem name="info" class="dropdown-item">
						<Icon type="ios-person-outline" />
						个人中心
					</DropdownItem>
					<DropdownItem name="pwd" class="dropdown-item">
						<Icon type="ios-lock-outline" />
						修改密码
					</DropdownItem>
					<DropdownItem name="exit" divided class="dropdown-item">
						<Icon type="ios-log-out" />
						退出系统
					</DropdownItem>
				</DropdownMenu>
			</template>
		</Dropdown>

		<Modal v-model="showInfoFlag"
			title="个人中心" 
			ok-text="保存" 
			cancel-text="取消" 
			@on-ok="updInfo()"
			class="info-modal">
			<Form :label-width="80" :model="infoForm" class="info-form">
				<FormItem label="用户账号">
					<Input v-model="infoForm.userName" placeholder="请输入用户账号..." class="form-input"></Input>
				</FormItem>
				<FormItem label="用户姓名">
					<Input v-model="infoForm.name" placeholder="请输入用户姓名..." class="form-input"></Input>
				</FormItem>
				<FormItem label="用户年龄">
					<Input v-model="infoForm.age" placeholder="请输入用户年龄..." class="form-input"></Input>
				</FormItem>
				<FormItem label="用户性别">
					<RadioGroup v-model="infoForm.gender" class="gender-group">
						<Radio label="男" class="gender-radio">男</Radio>
						<Radio label="女" class="gender-radio">女</Radio>
					</RadioGroup>
				</FormItem>
			</Form>
		</Modal>

		<Modal v-model="showPwdFlag"
			title="修改密码" 
			ok-text="确认修改" 
			cancel-text="取消" 
			@on-ok="updPwd()"
			class="pwd-modal">
			<Form :label-width="80" :model="pwdForm" class="pwd-form">
				<FormItem label="原始密码">
					<Input v-model="pwdForm.oldPwd" type="password" placeholder="请输入原始密码..." class="form-input"></Input>
				</FormItem>
				<FormItem label="新密码">
					<Input v-model="pwdForm.newPwd" type="password" placeholder="请输入新密码..." class="form-input"></Input>
				</FormItem>
				<FormItem label="确认密码">
					<Input v-model="pwdForm.rePwd" type="password" placeholder="请再次输入新密码..." class="form-input"></Input>
				</FormItem>
			</Form>
		</Modal>
	</Header>
</template>

<style>
.fater-header-user {
	display: flex;
	align-items: center;
	justify-content: flex-end;
	padding: 0 20px;
}

.user-dropdown {
	margin-left: auto;
}

.user-info {
	display: flex;
	align-items: center;
	padding: 8px 15px;
	background: rgba(255, 255, 255, 0.1);
	border-radius: 25px;
	color: #fff;
	text-decoration: none;
	transition: all 0.3s ease;
	border: 1px solid rgba(255, 255, 255, 0.2);
}

.user-info:hover {
	background: rgba(255, 255, 255, 0.2);
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-avatar {
	margin-right: 8px;
	background: rgba(255, 255, 255, 0.2);
}

.user-text {
	font-size: 14px;
	font-weight: 500;
	margin-right: 5px;
}

.dropdown-icon {
	font-size: 12px;
	transition: transform 0.3s ease;
}

.user-dropdown:hover .dropdown-icon {
	transform: rotate(180deg);
}

.user-dropdown-menu {
	border-radius: 8px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
	border: none;
	overflow: hidden;
}

.dropdown-item {
	display: flex;
	align-items: center;
	padding: 12px 16px;
	transition: all 0.3s ease;
}

.dropdown-item:hover {
	background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
	color: #fff;
}

.dropdown-item i {
	margin-right: 8px;
	font-size: 16px;
}

/* 模态框样式 */
.info-modal .ivu-modal-header,
.pwd-modal .ivu-modal-header {
	background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
	color: #fff;
	border-radius: 8px 8px 0 0;
}

.info-modal .ivu-modal-header-inner,
.pwd-modal .ivu-modal-header-inner {
	color: #fff;
	font-weight: 600;
}

.info-form,
.pwd-form {
	padding: 20px 0;
}

.form-input {
	border-radius: 6px;
	border: 1px solid #e8eaec;
	transition: all 0.3s ease;
}

.form-input:hover {
	border-color: #1890ff;
}

.form-input:focus {
	border-color: #1890ff;
	box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.gender-group {
	display: flex;
	gap: 20px;
}

.gender-radio {
	margin-right: 0;
}

.gender-radio .ivu-radio-inner {
	border-radius: 50%;
	border: 2px solid #e8eaec;
	transition: all 0.3s ease;
}

.gender-radio .ivu-radio-checked .ivu-radio-inner {
	border-color: #1890ff;
	background: #1890ff;
}

.gender-radio .ivu-radio-checked .ivu-radio-inner::after {
	background: #fff;
}

/* 响应式设计 */
@media (max-width: 768px) {
	.user-text {
		display: none;
	}
	
	.user-info {
		padding: 8px 12px;
	}
	
	.dropdown-item {
		padding: 10px 12px;
	}
}
</style>

<script>
import {
	exit,
	getLoginUser,
	updSessionInfo,
	updSessionPwd,
} from "../api";

export default {
	data() {
		return {
			showInfoFlag: false,
			showPwdFlag: false,
			pwdForm: {
				token: this.$store.state.token,
				newPwd: "",
				rePwd: "",
				oldPwd: ""
			},
			infoForm: {
				token: this.$store.state.token,
				userName: "",
				name: "",
				gender: "",
				age: "",
			},
		}
	},
	methods: {
		showInfoWin(){

			getLoginUser(this.$store.state.token).then(resp =>{

				this.infoForm.userName = resp.data.userName;
				this.infoForm.name = resp.data.name;
				this.infoForm.gender = resp.data.gender;
				this.infoForm.age = resp.data.age;

				this.showInfoFlag = true;
			});
		},
		showPwdWin(){

			this.pwdForm = {
				token: this.$store.state.token,
				newPwd: "",
				rePwd: "",
				oldPwd: ""
			};
			this.showPwdFlag = true;
		},
		handleUser(name) {

			if (name == "info") {
					
				this.showInfoWin();
			} else if (name == "pwd") {
				
				this.showPwdWin();
			} else if (name == "exit") {
				
				this.$Modal.confirm({
					title: '确认修改',
					content: '确定要退出系统吗？',
					onOk: () => {

                        exit(this.$store.state.token)
                          .finally(() => {
                            // 不论接口结果如何，统一本地退出
                            this.$store.commit("clearToken");
                            this.$store.commit("clearMenus");
                            sessionStorage.clear();
                            window.location.href = "/";
                          });
					},
            	});
			}
		},
		updInfo(){

			updSessionInfo(this.infoForm).then(resp =>{

				if(resp.code == 0){

					this.$Message.success({
						background: true,
						content: '用户信息修改完成'
					});
					this.showInfoFlag = false;
				}else{
					
					this.$Message.warning({
						background: true,
						content: resp.msg
					});
					this.showInfoFlag = true;
				}
			});
		},
		updPwd(){

			updSessionPwd(this.pwdForm).then(resp =>{

				if(resp.code == 0){

					this.$Message.success({
						background: true,
						content: '用户密码修改完成'
					});
					this.showPwdFlag = false;
				}else{
					
					this.$Message.warning({
						background: true,
						content: resp.msg
					});
					this.showPwdFlag = true;
				}
			});
		},
	},
}
</script>
