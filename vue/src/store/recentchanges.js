import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall, makeURLQueryParams } from '@/plugins/swagger.js';
import { displayErrorNotification } from '@/helpers/notifications';
import { asVersion } from '@/helpers/casl';

Vue.use( Vuex );

export const actions = {
	/**
	 * fetch recent changes and update RECENT_CHANGES state with the results obtained via the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} payload
	 * @param {string} payload.user - user filter. value is username of the user responsible
	 * for the revision.
	 * @param {string} payload.target_type - target_type filter.
	 * value is either "tool" or "toollist".
	 * @param {boolean} payload.suppressed - suppressed filter. either true or null.
	 * @param {boolean} payload.unpatrolled - unpatrolled filter. either true or null.
	 * @param {string} payload.date_created_after - used to filter for all revisions
	 * from this point in time up to another point in time in the future relative to this.
	 * @param {string} payload.date_created_before - used to filter for all revisions from a
	 * certain point in time in the past to this point in time.
	 * @param {number} payload.page - for pagination.
	 * @return {Promise<undefined>}
	 */
	fetchRecentChanges( context, payload ) {

		// endpoint expects patrolled key.
		// convert unpatrolled from filter to patrolled key.
		const patrolled = payload.unpatrolled ? false : null;

		const params = [
			[ 'user', payload.user ],
			[ 'target_type', payload.target_type ],
			[ 'suppressed', payload.suppressed ],
			[ 'patrolled', patrolled ],
			[ 'date_created_after', payload.date_created_after ],
			[ 'date_created_before', payload.date_created_before ],
			[ 'page', payload.page ]
		];

		const cleanParams = makeURLQueryParams( params );

		const request = { url: '/api/recent/?' + cleanParams.toString() };

		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'RECENT_CHANGES', success.body );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	}
};

export const mutations = {
	RECENT_CHANGES( state, changes ) {
		state.recentChanges = asVersion( changes.results );
		state.numChanges = changes.count;
	}
};

export default {
	namespaced: true,
	state: {
		recentChanges: [],
		numChanges: 0
	},
	actions: actions,
	mutations: mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
