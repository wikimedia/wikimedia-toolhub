import Vue from 'vue';
import Vuex from 'vuex';
import SwaggerClient from 'swagger-client';

Vue.use( Vuex );

export default {
	namespaced: true,
	state: {
		toolsList: [],
		toolInfo: [],
		numTools: 0,
		apiErrorMsg: ''
	},
	mutations: {
		TOOLS_LIST( state, tools ) {
			state.toolsList = tools.results;
			state.numTools = tools.count;
			state.apiErrorMsg = '';
		},
		TOOL_INFO( state, tool ) {
			state.toolInfo = tool;
			state.apiErrorMsg = '';
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
		getToolInfo( context, id ) {
			const request = {
				url: '/api/tools/' + id,
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			};

			SwaggerClient.http( request ).then( ( response ) => {
				context.commit( 'TOOL_INFO', response.body );
			} )
				.catch( ( err ) => context.commit( 'ERROR', err ) );
		}
	},
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
