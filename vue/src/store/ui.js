import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger.js';
import i18n from '@/plugins/i18n';

Vue.use( Vuex );

export const actions = {
	/**
	 * Get data specially chosen for the home screen.
	 *
	 * @param {Object} context - Vuex context
	 * @return {Promise}
	 */
	getHomeData( context ) {
		const request = { url: '/api/ui/home/' };

		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'onHomeData', success.body );
			},
			( failure ) => {
				const data = getFailurePayload( failure );
				for ( const err in data.errors ) {
					this._vm.$notify.error(
						i18n.t( 'apierrors', [
							data.errors[ err ].field,
							data.errors[ err ].message
						] )
					);
				}
			}
		);
	}
};

export const mutations = {
	/**
	 * Persist Home data..
	 *
	 * @param {Object} state - Vuex state tree.
	 * @param {Object} payload - mutation payload.
	 * @param {number} payload.total_tools - count of tools known to Toolhub
	 * @param {string} payload.last_crawl_time - date and time of latest run
	 * @param {number} payload.last_crawl_changed - tools changed in the latest run
	 */
	onHomeData( state, payload ) {
		state.totalTools = payload.total_tools;
		state.lastCrawlTime = payload.last_crawl_time;
		state.lastCrawlChanged = payload.last_crawl_changed;
	}
};

export default {
	namespaced: true,
	state: {
		totalTools: 0,
		lastCrawlTime: '',
		lastCrawlChanged: 0
	},
	actions: actions,
	mutations: mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
