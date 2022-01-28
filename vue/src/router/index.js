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
			name: 'tools-view',
			path: '/tools/:name([\\w%-]{1,255})',
			component: () => import( /* webpackChunkName: "tools-view" */ '../views/ToolView.vue' )
		},
		{
			name: 'tools-edit',
			path: '/tools/:name([\\w%-]{1,255})/edit',
			component: () => import( /* webpackChunkName: "tools-edit" */ '../views/EditTool.vue' )
		},
		{
			name: 'tools-history',
			path: '/tools/:name([\\w%-]{1,255})/history',
			component: () => import( /* webpackChunkName: "tools-history" */ '../views/ToolHistory.vue' )
		},
		{
			name: 'tools-revision',
			path: '/tools/:name([\\w%-]{1,255})/history/revision/:revId(\\d+)',
			component: () => import( /* webpackChunkName: "tools-revision" */ '../views/ToolView.vue' )
		},
		{
			name: 'tools-diff',
			path: '/tools/:name([\\w%-]{1,255})/history/revision/:revId(\\d+)/diff/:otherRevId(\\d+)',
			component: () => import( /* webpackChunkName: "tools-diff" */ '../views/ToolRevisionsDiff.vue' )
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
			name: 'favorites',
			path: '/favorites',
			component: () => import( /* webpackChunkName: "favorites" */ '../views/Favorites.vue' )
		},
		{
			name: 'lists',
			path: '/lists',
			component: () => import( /* webpackChunkName: "lists" */ '../views/Lists.vue' )
		},
		{
			name: 'lists-view',
			path: '/lists/:id(\\d+)',
			component: () => import( /* webpackChunkName: "lists-view" */ '../views/ListView.vue' )
		},
		{
			name: 'lists-edit',
			path: '/lists/:id(\\d+)/edit',
			component: () => import( /* webpackChunkName: "lists-edit" */ '../components/lists/CreateEditList.vue' )
		},
		{
			name: 'lists-create',
			path: '/lists/create',
			component: () => import( /* webpackChunkName: "lists-create" */ '../components/lists/CreateEditList.vue' )
		},
		{
			name: 'lists-history',
			path: '/lists/:id(\\d+)/history',
			component: () => import( /* webpackChunkName: "lists-history" */ '../views/ListHistory.vue' )
		},
		{
			name: 'lists-revision',
			path: '/lists/:id(\\d+)/history/revision/:revId(\\d+)',
			component: () => import( /* webpackChunkName: "lists-view" */ '../views/ListView.vue' )
		},
		{
			name: 'lists-diff',
			path: '/lists/:id(\\d+)/history/revision/:revId(\\d+)/diff/:otherRevId(\\d+)',
			component: () => import( /* webpackChunkName: "lists-diff" */ '../views/ListRevisionsDiff.vue' )
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
				icon: 'mdi-history'
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
			name: 'members',
			path: '/members',
			component: () => import( /* webpackChunkName: "members" */ '../views/Members.vue' ),
			meta: {
				icon: 'mdi-account-group'
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
