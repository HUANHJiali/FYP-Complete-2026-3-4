<template>
	<div class="fater-layout-left" :class="{ 'mobile-drawer': isMobile, 'mobile-open': isMobile && isOpen }">
		<div class="fater-header-logo">
			<Icon type="ios-school" class="logo-icon" />
			<span class="logo-text">在线考试管理系统</span>
		</div>
		<Sider class="menu-sider">
						<Menu theme="light" :active-name="'系统首页'" class="menu-container">
				<MenuItem
					v-for="(item, index) in menuList"
					:key="index"
					:name="item.name"
					:to="item.path"
					@click="onMenuItemClick"
					class="menu-item">
					<Icon :type="item.icon" class="menu-icon" />
					<span class="menu-text">{{ item.name }}</span>
				</MenuItem>
			</Menu>
		</Sider>
	</div>
</template>

<script>
export default{
    props: {
        menuList: [],
		isMobile: {
			type: Boolean,
			default: false
		},
		isOpen: {
			type: Boolean,
			default: false
		}
    },
	methods: {
		onMenuItemClick() {
			if (this.isMobile) {
				this.$emit('item-click');
			}
		}
    }
}
</script>

<style>
.fater-layout-left {
	position: fixed;
	top: 0px;
	left: 0;
	bottom: 0;
	background: #fff;
	box-shadow: 2px 0 10px rgba(0,0,0,0.1);
	width: 250px;
	z-index: 1000;
}

.fater-header-logo {
	height: 70px;
	width: 250px;
	text-align: center;
	line-height: 70px;
	font-size: 18px;
	font-weight: 600;
	color: #fff;
	background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
	border-right: 1px solid rgba(255,255,255,0.1);
	box-shadow: 2px 0 10px rgba(0,0,0,0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 10px;
}

.logo-icon {
	font-size: 24px;
	color: #fff;
}

.logo-text {
	font-size: 16px;
	font-weight: 600;
	color: #fff;
}

.menu-sider {
	background: #fff;
	height: calc(100vh - 70px);
	overflow-y: auto;
}

.menu-container {
	background: #fff;
	border-right: none;
	padding: 10px 0;
}

.menu-item {
	height: 50px;
	line-height: 50px;
	margin: 5px 10px;
	border-radius: 8px;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	padding: 0 15px;
	color: #666;
	font-weight: 500;
}

.menu-item:hover {
	background: linear-gradient(90deg, #1890ff 0%, #0050b3 100%);
	color: #fff;
	transform: translateX(5px);
	box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.menu-item.ivu-menu-item-active {
	background: linear-gradient(90deg, #1890ff 0%, #0050b3 100%);
	color: #fff;
	border-right: none;
	transform: translateX(5px);
	box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.menu-icon {
	font-size: 18px;
	margin-right: 12px;
	width: 20px;
	text-align: center;
}

.menu-text {
	font-size: 14px;
	font-weight: 500;
}

/* 滚动条样式 */
.menu-sider::-webkit-scrollbar {
	width: 4px;
}

.menu-sider::-webkit-scrollbar-track {
	background: transparent;
}

.menu-sider::-webkit-scrollbar-thumb {
	background: rgba(24, 144, 255, 0.3);
	border-radius: 2px;
}

.menu-sider::-webkit-scrollbar-thumb:hover {
	background: rgba(24, 144, 255, 0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
	.fater-layout-left.mobile-drawer {
		width: 250px;
		transform: translateX(-100%);
		transition: transform 0.25s ease;
		z-index: 1500;
	}

	.fater-layout-left.mobile-drawer.mobile-open {
		transform: translateX(0);
	}
	
	.fater-header-logo {
		width: 250px;
		font-size: 14px;
	}
	
	.logo-text {
		font-size: 14px;
	}
	
	.menu-item {
		margin: 3px 8px;
		padding: 0 12px;
	}
	
	.menu-icon {
		font-size: 16px;
		margin-right: 10px;
	}
	
	.menu-text {
		font-size: 13px;
	}
}
</style>
