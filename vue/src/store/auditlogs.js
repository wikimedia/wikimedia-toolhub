import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall } from '@/plugins/swagger.js';
import { displayErrorNotification } from '@/helpers/notifications';

Vue.use( Vuex );

export const actions = {
	fetchAuditLogs( context, payload ) {
		const filters = payload.filters;

		const params = [
			[ 'target_type', filters.target_type ],
			[ 'user', filters.user ],
			[ 'after', filters.after ],
			[ 'before', filters.before ],
			[ 'page', payload.page ]
		];

		const cleanParams = new URLSearchParams(
			params.filter( ( value ) => {
				const val = value[ 1 ];
				return val !== null && val !== undefined;
			} )
		);

		const request = { url: '/api/auditlogs/?' + cleanParams.toString() };

		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'AUDIT_LOGS', success.body );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	}
};

export const mutations = {
	AUDIT_LOGS( state, logs ) {
		state.auditLogs = logs.results;
		state.numLogs = logs.count;
	}
};

export default {
	namespaced: true,
	state: {
		auditLogs: [],
		numLogs: 0
	},
	actions: actions,
	mutations: mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
