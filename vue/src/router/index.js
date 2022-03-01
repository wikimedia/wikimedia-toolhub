import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '../views/Home.vue';

Vue.use( VueRouter );

const AddRemoveTools = () => import( /* webpackChunkName: "addremovetools" */ '../views/AddRemoveTools.vue' );
const ApiDocs = () => import( /* webpackChunkName: "apidoc" */ '../views/ApiDocs.vue' );
const AuditLogs = () => import( /* webpackChunkName: "auditlogs" */ '../views/AuditLogs.vue' );
const CrawlerHistory = () => import( /* webpackChunkName: "crawlerhistory" */ '../views/CrawlerHistory.vue' );
const CreateEditList = () => import( /* webpackChunkName: "lists-edit" */ '../components/lists/CreateEditList.vue' );
const DeveloperSettings = () => import( /* webpackChunkName: "developersettings" */ '../views/DeveloperSettings.vue' );
const EditTool = () => import( /* webpackChunkName: "tools-edit" */ '../views/EditTool.vue' );
const Favorites = () => import( /* webpackChunkName: "favorites" */ '../views/Favorites.vue' );
const ListHistory = () => import( /* webpackChunkName: "lists-history" */ '../views/ListHistory.vue' );
const ListRevisionsDiff = () => import( /* webpackChunkName: "lists-diff" */ '../views/ListRevisionsDiff.vue' );
const ListView = () => import( /* webpackChunkName: "lists-view" */ '../views/ListView.vue' );
const Lists = () => import( /* webpackChunkName: "lists" */ '../views/MyLists.vue' );
const PublishedLists = () => import( /* webpackChunkName: "publishedlists" */ '../views/PublishedLists.vue' );
const Members = () => import( /* webpackChunkName: "members" */ '../views/Members.vue' );
const Search = () => import( /* webpackChunkName: "search" */ '../views/Search.vue' );
const ToolHistory = () => import( /* webpackChunkName: "tools-history" */ '../views/ToolHistory.vue' );
const ToolRevisionsDiff = () => import( /* webpackChunkName: "tools-diff" */ '../views/ToolRevisionsDiff.vue' );
const ToolView = () => import( /* webpackChunkName: "tools-view" */ '../views/ToolView.vue' );

export const routes = [
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
		component: ToolView
	},
	{
		name: 'tools-edit',
		path: '/tools/:name([\\w%-]{1,255})/edit',
		component: EditTool
	},
	{
		name: 'tools-history',
		path: '/tools/:name([\\w%-]{1,255})/history',
		component: ToolHistory
	},
	{
		name: 'tools-revision',
		path: '/tools/:name([\\w%-]{1,255})/history/revision/:revId(\\d+)',
		component: ToolView
	},
	{
		name: 'tools-diff',
		path: '/tools/:name([\\w%-]{1,255})/history/revision/:revId(\\d+)/diff/:otherRevId(\\d+)',
		component: ToolRevisionsDiff
	},
	{
		name: 'addremovetools',
		path: '/add-or-remove-tools',
		component: AddRemoveTools,
		meta: {
			icon: 'mdi-folder-multiple-plus-outline'
		}
	},
	{
		name: 'favorites',
		path: '/favorites',
		component: Favorites
	},
	{
		name: 'lists',
		path: '/lists',
		component: Lists
	},
	{
		name: 'lists-view',
		path: '/lists/:id(\\d+)',
		component: ListView
	},
	{
		name: 'lists-edit',
		path: '/lists/:id(\\d+)/edit',
		component: CreateEditList
	},
	{
		name: 'lists-create',
		path: '/lists/create',
		component: CreateEditList
	},
	{
		name: 'lists-history',
		path: '/lists/:id(\\d+)/history',
		component: ListHistory
	},
	{
		name: 'lists-revision',
		path: '/lists/:id(\\d+)/history/revision/:revId(\\d+)',
		component: ListView
	},
	{
		name: 'lists-diff',
		path: '/lists/:id(\\d+)/history/revision/:revId(\\d+)/diff/:otherRevId(\\d+)',
		component: ListRevisionsDiff
	},
	{
		name: 'publishedlists',
		path: '/published-lists',
		component: PublishedLists,
		meta: {
			icon: 'mdi-view-list'
		}
	},
	{
		name: 'apidocs',
		path: '/api-docs',
		component: ApiDocs,
		meta: {
			icon: 'mdi-api'
		}
	},
	{
		name: 'crawlerhistory',
		path: '/crawler-history',
		component: CrawlerHistory,
		meta: {
			icon: 'mdi-history'
		}
	},
	{
		name: 'auditlogs',
		path: '/audit-logs',
		component: AuditLogs,
		meta: {
			icon: 'mdi-data-matrix'
		}
	},
	{
		name: 'members',
		path: '/members',
		component: Members,
		meta: {
			icon: 'mdi-account-group'
		}
	},
	{
		name: 'developersettings',
		path: '/developer-settings',
		component: DeveloperSettings
	},
	{
		name: 'search',
		path: '/search',
		component: Search
	}
];

/**
 * Handle scrolling on navigation.
 *
 * @param {Object} to - Route being navigated to
 * @param {Object} from - Route being navigated from
 * @param {?Object} savedPosition - Popstate navigation prior position
 * @return {Object}
 */
export function scrollBehavior( to, from, savedPosition ) {
	if ( savedPosition ) {
		return savedPosition;
	}
	if ( to.hash ) {
		return { selector: to.hash };
	}
	return { x: 0, y: 0 };
}

export default new VueRouter( {
	mode: 'history',
	base: '/',
	routes,
	scrollBehavior
} );
