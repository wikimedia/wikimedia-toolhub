import Vue from 'vue';
import Vuex from 'vuex';
import SwaggerClient from 'swagger-client';

import {
	OPENAPI_SCHEMA_URL,
	makeApiCall
} from '@/plugins/swagger';
import { displayErrorNotification } from '@/helpers/notifications';

Vue.use( Vuex );

export const getters = {};

export const actions = {
	/**
	 * Load the backend server's OpenAPI spec.
	 *
	 * @param {Object} context - Vuex context
	 * @param {boolean} invalidateCache - Force fetching schema if true
	 * @return {Promise<Object>}
	 */
	fetchOpenAPISchema( context, invalidateCache = false ) {
		// Avoid loading the raw schema if we already have it in cache
		if ( !invalidateCache && context.state.schemaPromise ) {
			return context.state.schemaPromise;
		}

		const promise = makeApiCall(
			context, { url: OPENAPI_SCHEMA_URL }
		).then( ( response ) => {
			const spec = response.body;
			return SwaggerClient.resolve( { spec } );
		} ).then( ( { spec } ) => {
			context.commit( 'onSpecChanged', { spec } );
			return spec;
		} ).catch( ( failure ) => {
			displayErrorNotification.call( this, failure );
		} );

		context.commit( 'SCHEMA_PROMISE', promise );
		return promise;
	},

	/**
	 * Get an API operation schema.
	 *
	 * @param {Object} context - Vuex state
	 * @param {string} opId - Operation id (e.g. 'tools_create')
	 * @return {Promise<Object|undefined>}
	 */
	getOperationSchema( context, opId ) {
		return context.dispatch( 'fetchOpenAPISchema' ).then( ( api ) => {
			for ( const pathName in api.paths ) {
				const path = api.paths[ pathName ];
				for ( const method in path ) {
					const operation = path[ method ];
					if ( operation.operationId === opId ) {
						return operation;
					}
				}
			}
			throw new Error( `Operation ${opId} not found` );
		} );
	},

	/**
	 * Get the schema for the request body of an operation.
	 *
	 * @param {Object} context - Vuex state
	 * @param {string} opId - Operation id (e.g. 'tools_create')
	 * @return {Promise<Object|undefined>}
	 */
	getRequestSchema( context, opId ) {
		return context.dispatch( 'getOperationSchema', opId ).then(
			( data ) => {
				const body = data.requestBody.content[ 'application/json' ];
				return { ...body.schema };
			}
		);
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
	},
	SCHEMA_PROMISE( state, promise ) {
		state.schemaPromise = promise;
	}
};

export default {
	namespaced: true,
	state: {
		apispec: null,
		schemaPromise: null
	},
	getters: getters,
	actions: actions,
	mutations: mutations,
	strict: process.env.NODE_ENV !== 'production'
};
