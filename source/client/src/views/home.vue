<template>
    	<Layout>
		<Menus :menuList="($store.state.menus && $store.state.menus.children) || []"></Menus>
		<Layout>
			<Header class="fater-header">
				<Breadcrumb v-if="$route.name !== 'welcome'" class="fater-header-nav">
					<BreadcrumbItem :to="{ name: 'welcome' }">系统首页</BreadcrumbItem>
					<BreadcrumbItem>{{ getCurrentPageTitle() }}</BreadcrumbItem>
				</Breadcrumb>
				<Nav></Nav>
			</Header>
			<Content class="fater-layout-body">
				<router-view></router-view>
			</Content>
		</Layout>
	</Layout>
</template>

<style>

</style>

<script>
import Nav from "../components/nav.vue";
import Menus from "../components/menus.vue";

export default {
	components: {
		Nav,
		Menus
	},
	methods: {
		getCurrentPageTitle() {
			// 根據當前路由獲取頁面標題（增加空值保護，避免登出時 menus 為 null 報錯）
			const currentRoute = (this.$router && this.$router.currentRoute && this.$router.currentRoute.value) || this.$route || {};
			const menus = (this.$store && this.$store.state && this.$store.state.menus) || null;
			const menuList = (menus && menus.children) || [];
			// 查找對應的菜單項（按 path 或 name 匹配）
			const menuItem = menuList.find(item => item.path === currentRoute.path || item.name === currentRoute.name);
			if (menuItem) {
				return menuItem.name || menuItem.title || '';
			}
			// 如果沒有找到，返回路由 meta 標題或名稱，否則空字符串避免 UI 報錯
			return (currentRoute.meta && currentRoute.meta.title) || currentRoute.name || '';
		}
	}
}
</script>
