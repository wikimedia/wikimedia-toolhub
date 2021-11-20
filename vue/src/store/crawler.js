import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger';
import i18n from '@/plugins/i18n';
import { asUrl } from '@/helpers/casl';

Vue.use( Vuex );

export const actions = {
	async fetchCrawlerHistory( context, page ) {
		let history = [];
		const request1 = { url: '/api/crawler/runs/?page=' + page };

		makeApiCall( context, request1 ).then(
			( success1 ) => {
				history = success1.body;
				context.commit( 'CRAWLER_HISTORY', history );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error( i18n.t( 'apierror', [ explanation ] ) );
			}
		);
	},

	fetchCrawlerUrls( context, data ) {
		const request = {
			url: '/api/crawler/runs/' + data.runId + '/urls/?page=' + data.page
		};

		makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'CRAWLER_URLS', success.body );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error( i18n.t( 'apierror', [ explanation ] ) );
			}
		);
	},
	registerUrl( context, url ) {
		if ( !context.rootState.user.user.is_authenticated ) {
			return;
		}
		const request = {
			url: '/api/crawler/urls/',
			method: 'POST',
			body: JSON.stringify( { url: url } )
		};
		makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'REGISTER_URL', success.body );
				this._vm.$notify.success( i18n.t( 'toolurlregistrationsuccess' ) );
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
	},
	unregisterUrl( context, urlObj ) {
		if ( !context.rootState.user.user.is_authenticated ) {
			return;
		}
		const request = {
			url: '/api/crawler/urls/' + urlObj.id + '/',
			method: 'DELETE'
		};

		makeApiCall( context, request ).then(
			() => {
				context.commit( 'UNREGISTER_URL', urlObj.url );
				this._vm.$notify.success( i18n.t( 'toolurlunregistrationsuccess' ) );
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
	},
	getUrlsCreatedByUser( context, page ) {
		if ( !context.rootState.user.user.is_authenticated ) {
			this._vm.$notify.info(
				i18n.t( 'addremovetools-nologintext' )
			);
			return;
		}
		const request = {
			url: '/api/crawler/urls/self/?page=' + page,
			method: 'GET'
		};

		makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'USER_CREATED_URLS', success.body );
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
