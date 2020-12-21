import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '../views/Home.vue';

Vue.use( VueRouter );
Vue.use( require( 'vue-moment' ) );

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
			path: '/tool/:id/',
			component: () => import( /* webpackChunkName: "tool" */ '../views/Tool.vue' )
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
		}
	],

	router = new VueRouter( {
		mode: 'history',
		base: '/',
		routes
	} );

export default router;
