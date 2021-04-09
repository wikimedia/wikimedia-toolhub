import Vue from 'vue';
import Vuex from 'vuex';
import makeApiCall from '@/plugins/swagger.js';
import i18n from '@/plugins/i18n';

Vue.use( Vuex );

export default {
	namespaced: true,
	state: {
		auditLogs: [],
		numLogs: 0
	},
	mutations: {
		AUDIT_LOGS( state, logs ) {
			state.auditLogs = logs.results;
			state.numLogs = logs.count;
		}
	},
	actions: {
		fetchAuditLogs( context, page ) {
			const request = { url: '/api/auditlogs/?page=' + page };

			makeApiCall( context, request ).then(
				( success ) => {
					context.commit( 'AUDIT_LOGS', success.body );
				},
				( failure ) => {
					const explanation = ( 'statusCode' in failure ) ?
						failure.response.statusText : failure;

					this._vm.$notify.error( i18n.t( 'auditlogs-apierror', [ page, explanation ] ) );
				}
			);
		}
	},
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
