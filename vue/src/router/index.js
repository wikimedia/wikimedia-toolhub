import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '../views/Home.vue';

Vue.use( VueRouter );

const routes = [
		{
			name: 'home',
			path: '/',
			component: Home,
			meta: {
				icon: 'mdi-home-circle'
			}
		},
		{
			name: 'tool',
			path: '/tool/:name([\\w-]{1,255})',
			component: () => import( /* webpackChunkName: "tool" */ '../views/Tool.vue' )
		},
		{
			name: 'edittool',
			path: '/tool/:name([\\w-]{1,255})/edit',
			component: () => import( /* webpackChunkName: "edittool" */ '../views/EditTool.vue' )
		},
		{
			name: 'addremovetools',
			path: '/add-or-remove-tools',
			component: () => import( /* webpackChunkName: "addremovetools" */ '../views/AddRemoveTools.vue' ),
			meta: {
				icon: 'mdi-folder-multiple-plus-outline'
			}
		},
		{
			name: 'apidocs',
			path: '/api-docs',
			component: () => import( /* webpackChunkName: "apidoc" */ '../views/ApiDocs.vue' ),
			meta: {
				icon: 'mdi-api'
			}
		},
		{
			name: 'crawlerhistory',
			path: '/crawler-history',
			component: () => import( /* webpackChunkName: "crawlerhistory" */ '../views/CrawlerHistory.vue' ),
			meta: {
				icon: 'mdi-bug'
			}
		},
		{
			name: 'auditlogs',
			path: '/audit-logs',
			component: () => import( /* webpackChunkName: "auditlogs" */ '../views/AuditLogs.vue' ),
			meta: {
				icon: 'mdi-data-matrix'
			}
		},
		{
			name: 'developersettings',
			path: '/developer-settings',
			component: () => import( /* webpackChunkName: "developersettings" */ '../views/DeveloperSettings.vue' )
		},
		{
			name: 'search',
			path: '/search',
			component: () => import( /* webpackChunkName: "search" */ '../views/Search.vue' )
		}
	],

	router = new VueRouter( {
		mode: 'history',
		base: '/',
		routes,
		scrollBehavior( to, from, savedPosition ) {
			if ( savedPosition ) {
				return savedPosition;
			}
			if ( to.hash ) {
				return { selector: to.hash };
			}
			return { x: 0, y: 0 };
		}
	} );

export default router;
