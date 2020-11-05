import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '../views/Home.vue';

Vue.use( VueRouter );
Vue.use( require( 'vue-moment' ) );

const routes = [
		{
			name: 'home',
			title: 'Home',
			path: '/',
			component: Home,
			meta: {
				icon: 'mdi-home-circle'
			}
		},
		{
			name: 'add-or-remove-tools',
			title: 'Add or remove tools',
			path: '/add-or-remove-tools',
			component: () => import( /* webpackChunkName: "addremovetools" */ '../views/AddRemoveTools.vue' ),
			meta: {
				icon: 'mdi-folder-multiple-plus-outline'
			}
		},
		{
			name: 'api-docs',
			title: 'API docs',
			path: '/api-docs',
			component: () => import( /* webpackChunkName: "apidoc" */ '../views/ApiDocs.vue' ),
			meta: {
				icon: 'mdi-api'
			}
		},
		{
			name: 'about',
			title: 'About',
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
