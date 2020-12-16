import Vue from 'vue';
import Vuex from 'vuex';
import SwaggerClient from 'swagger-client';

Vue.use( Vuex );

export default {
	namespaced: true,
	state: {
		auditLogs: [],
		numLogs: 0,
		apiErrorMsg: ''
	},
	mutations: {
		AUDIT_LOGS( state, logs ) {
			state.auditLogs = logs.results;
			state.numLogs = logs.count;
			state.apiErrorMsg = '';
		},
		ERROR( state, error ) {
			state.apiErrorMsg = error;
		}
	},
	actions: {
		async makeApiCall( context, url ) {
			let data,
				error = '';

			try {
				data = await SwaggerClient.http( {
					url: url,
					method: 'GET',
					headers: {
						'Content-Type': 'application/json'
					}
				} );
			} catch ( err ) {
				error = err;
			}

			return { data: data, error: error };
		},
		async fetchAuditLogs( context, page ) {
			const url = '/api/auditlogs/?page=' + page;
			const resp = await context.dispatch( 'makeApiCall', url );

			if ( resp.error ) {
				context.commit( 'ERROR', resp.error );
				return;
			}

			context.commit( 'AUDIT_LOGS', resp.data && resp.data.body );
		}
	},
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
