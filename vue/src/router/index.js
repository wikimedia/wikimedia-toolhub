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
			name: 'about',
			path: '/about',
			// route level code-splitting
			// this generates a separate chunk (about.[hash].js) for this route
			// which is lazy-loaded when the route is visited.
			component: () => import( /* webpackChunkName: "about" */ '../views/About.vue' ),
			meta: {
				icon: 'mdi-information-outline'
			}
		}
	],

	router = new VueRouter( {
		mode: 'history',
		base: '/',
		routes
	} );

export default router;
