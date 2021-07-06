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
			component: () => import( /* webpackChunkName: "tool" */ '../views/ToolView.vue' )
		},
		{
			name: 'edittool',
			path: '/tool/:name([\\w-]{1,255})/edit',
			component: () => import( /* webpackChunkName: "edittool" */ '../views/EditTool.vue' )
		},
		{
			name: 'toolhistory',
			path: '/tool/:name([\\w-]{1,255})/history',
			component: () => import( /* webpackChunkName: "toolhistory" */ '../views/ToolHistory.vue' )
		},
		{
			name: 'toolrevision',
			path: '/tool/:name([\\w-]{1,255})/history/revision/:revId',
			component: () => import( /* webpackChunkName: "toolrevision" */ '../views/ToolView.vue' )
		},
		{
			name: 'revisionsdiff',
			path: '/tool/:name([\\w-]{1,255})/history/revision/:revId/diff/:otherRevId/',
			component: () => import( /* webpackChunkName: "revisionsdiff" */ '../views/RevisionsDiff.vue' )
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
			name: 'lists',
			path: '/lists',
			component: () => import( /* webpackChunkName: "lists" */ '../views/Lists.vue' )
		},
		{
			name: 'list',
			path: '/list/:id',
			component: () => import( /* webpackChunkName: "list" */ '../components/lists/ListInfo.vue' )
		},
		{
			name: 'lists-create',
			path: '/lists/create',
			component: () => import( /* webpackChunkName: "createnewlist" */ '../components/lists/CreateNewList.vue' )
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
