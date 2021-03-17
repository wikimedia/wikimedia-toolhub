import Vue from 'vue';
import Vuex from 'vuex';

import SwaggerClient from 'swagger-client';

import i18n from '@/plugins/i18n';
import router from '@/router';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger.js';

Vue.use( Vuex );

export default {
	namespaced: true,
	state: {
		toolsList: [],
		tool: null,
		numTools: 0,
		apiErrorMsg: '',
		spdxLicenses: [],
		toolCreated: {}
	},
	mutations: {
		TOOLS_LIST( state, tools ) {
			state.toolsList = tools.results;
			state.numTools = tools.count;
			state.apiErrorMsg = '';
		},
		TOOL( state, tool ) {
			state.tool = tool;
		},
		SPDX_LICENSES( state, data ) {
			state.spdxLicenses = data;
		},
		CREATE_TOOL( state, tool ) {
			state.toolCreated = tool;
		},
		ERROR( state, error ) {
			state.apiErrorMsg = error;
		}
	},
	actions: {
		listAllTools( context, page ) {
			const request = {
				url: '/api/tools/?page_size=12&page=' + page,
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			};

			SwaggerClient.http( request ).then( ( response ) => {
				context.commit( 'TOOLS_LIST', response.body );
			} )
				.catch( ( err ) => context.commit( 'ERROR', err ) );
		},

		/**
		 * Fetch information for a single tool from the API.
		 *
		 * @param {Object} context - vuex context
		 * @param {string} name - tool name
		 * @return {Promise}
		 */
		getToolByName( context, name ) {
			const request = {
				url: '/api/tools/' + encodeURI( name )
			};

			return makeApiCall( context, request ).then(
				( response ) => {
					context.commit( 'TOOL', response.body );
				},
				( failure ) => {
					const data = getFailurePayload( failure );
					if ( data.status_code === 404 ) {
						this._vm.$notify.warning(
							i18n.t( 'tool-not-found', [ name ] )
						);
					} else {
						this._vm.$notify.error(
							i18n.t( 'apierror', [ data.message ] )
						);
					}
				}
			);
		},
		getSpdxLicenses( context ) {
			const request = {
				url: '/api/spdx/',
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			};

			SwaggerClient.http( request ).then( ( response ) => {
				context.commit( 'SPDX_LICENSES', response.body );
			} )
				.catch( ( err ) => context.commit( 'ERROR', err ) );
		},
		createTool( context, toolInfo ) {
			const request = {
				url: '/api/tools/',
				method: 'POST',
				body: JSON.stringify( toolInfo )
			};

			makeApiCall( context, request ).then(
				( success ) => {
					const data = success.body;
					context.commit( 'CREATE_TOOL', data );
					router.push( { path: '/tool/' + data.name } );

					this._vm.$notify.success(
						i18n.t( 'addremovetools-toolcreationsuccess', [ data.name ] ), 30000
					);
				},
				( failure ) => {
					const explanation = ( 'statusCode' in failure ) ?
						failure.response.statusText : failure;

					this._vm.$notify.error(
						i18n.t( 'apierror', [ explanation ] )
					);
				}
			);
		}
	},
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
