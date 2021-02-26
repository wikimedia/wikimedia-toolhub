import Vue from 'vue';
import Vuex from 'vuex';
import { client } from '@/plugins/swagger';

Vue.use( Vuex );

export const getters = {};

export const actions = {
	/**
	 * Load the backend server's OpenAPI spec.
	 *
	 * @param {Object} context - Vuex context
	 * @return {Promise<Object>}
	 */
	fetchOpenAPISchema( context ) {
		return client.then( ( api ) => {
			context.commit( 'onSpecChanged', { spec: api.spec } );
			return api.spec;
		} );
	},

	/**
	 * Get an API operation schema.
	 *
	 * @param {Object} context - Vuex state
	 * @param {string} opId - Operation id (e.g. 'tools_create')
	 * @return {Promise<Object|undefined>}
	 */
	getOperationSchema( context, opId ) {
		return client.then( ( api ) => {
			for ( const pathName in api.spec.paths ) {
				const path = api.spec.paths[ pathName ];
				for ( const method in path ) {
					const operation = path[ method ];
					if ( operation.operationId === opId ) {
						return operation;
					}
				}
			}
			return undefined;
		} );
	}
};

export const mutations = {
	/**
	 * Persist an OpenAPI spec change.
	 *
	 * @param {Object} state - Vuex state tree.
	 * @param {Object} payload - mutation payload.
	 * @param {Object} payload.spec - OpenAPI spec
	 */
	onSpecChanged( state, { spec } ) {
		state.apispec = spec;
	}
};

export default {
	namespaced: true,
	state: {
		apispec: {}
	},
	getters: getters,
	actions: actions,
	mutations: mutations,
	strict: process.env.NODE_ENV !== 'production'
};
