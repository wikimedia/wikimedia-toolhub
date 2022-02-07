import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall, makeURLQueryParams } from '@/plugins/swagger';
import i18n from '@/plugins/i18n';
import { asUrl } from '@/helpers/casl';
import { displayErrorNotification } from '@/helpers/notifications';

Vue.use( Vuex );

export const actions = {
	async fetchCrawlerHistory( context, payload ) {

		const filters = payload.filters;
		const params = [
			[ 'page', payload.page ],
			[ 'ordering', filters.runs_ordering ]
		];

		const cleanParams = makeURLQueryParams( params );

		let history = [];
		const request1 = { url: '/api/crawler/runs/?' + cleanParams.toString() };

		return makeApiCall( context, request1 ).then(
			( success1 ) => {
				history = success1.body;
				context.commit( 'CRAWLER_HISTORY', history );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},

	fetchCrawlerUrls( context, payload ) {

		const filters = payload.filters;
		const params = [
			[ 'page', payload.page ],
			[ 'ordering', filters.urls_ordering ]
		];

		const cleanParams = makeURLQueryParams( params );

		const request = {
			url: '/api/crawler/runs/' + payload.runId + '/urls/?' + cleanParams.toString()
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'CRAWLER_URLS', success.body );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	registerUrl( context, url ) {
		if ( !context.rootState.user.user.is_authenticated ) {
			return Promise.resolve();
		}
		const request = {
			url: '/api/crawler/urls/',
			method: 'POST',
			body: JSON.stringify( { url: url } )
		};
		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'REGISTER_URL', success.body );
				this._vm.$notify.success( i18n.t( 'toolurlregistrationsuccess' ) );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	unregisterUrl( context, urlObj ) {
		if ( !context.rootState.user.user.is_authenticated ) {
			return Promise.resolve();
		}
		const request = {
			url: '/api/crawler/urls/' + urlObj.id + '/',
			method: 'DELETE'
		};

		return makeApiCall( context, request ).then(
			() => {
				context.commit( 'UNREGISTER_URL', urlObj.url );
				this._vm.$notify.success( i18n.t( 'toolurlunregistrationsuccess' ) );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	getUrlsCreatedByUser( context, payload ) {
		if ( !context.rootState.user.user.is_authenticated ) {
			this._vm.$notify.info(
				i18n.t( 'addremovetools-nologintext' )
			);
			return Promise.resolve();
		}

		const filters = payload.filters;
		const params = [
			[ 'page', payload.page ],
			[ 'ordering', filters.ordering ]
		];

		const cleanParams = makeURLQueryParams( params );

		const request = {
			url: '/api/crawler/urls/self/?' + cleanParams.toString(),
			method: 'GET'
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'USER_CREATED_URLS', success.body );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	}
};

export const mutations = {
	CRAWLER_HISTORY( state, history ) {
		state.crawlerHistory = history.results;
		state.lastCrawlerRun = history.results[ 0 ];
		state.numCrawlerRuns = history.count;
	},
	CRAWLER_URLS( state, urls ) {
		state.crawlerUrls = urls.results;
		state.numCrawlerUrls = urls.count;
	},
	USER_CREATED_URLS( state, urls ) {
		state.userCreatedUrls = asUrl( urls.results );
		state.numUserCreatedUrls = urls.count;
	},
	REGISTER_URL( state, url ) {
		state.userCreatedUrls.push( asUrl( url ) );
		state.numUserCreatedUrls += 1;
	},
	UNREGISTER_URL( state, url ) {
		const index = state.userCreatedUrls.findIndex(
			( obj ) => obj.url === url
		);
		state.userCreatedUrls.splice( index, 1 );
		state.numUserCreatedUrls -= 1;
	}
};

export default {
	namespaced: true,
	state: {
		crawlerHistory: [],
		crawlerUrls: [],
		lastCrawlerRun: [],
		userCreatedUrls: [],
		numUserCreatedUrls: 0,
		numCrawlerRuns: 0,
		numCrawlerUrls: 0
	},
	actions,
	mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
