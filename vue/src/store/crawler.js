import Vue from 'vue';
import Vuex from 'vuex';
import makeApiCall from '@/plugins/swagger.js';

Vue.use( Vuex );

export default {
	namespaced: true,
	state: {
		crawlerHistory: [],
		crawlerUrls: [],
		lastCrawlerRun: [],
		numCrawlerRuns: 0,
		numCrawlerUrls: 0
	},
	mutations: {
		CRAWLER_HISTORY( state, history ) {
			state.crawlerHistory = history.results;
			state.lastCrawlerRun = history.results[ 0 ];
			state.numCrawlerRuns = history.count;
		},
		CRAWLER_URLS( state, urls ) {
			state.crawlerUrls = urls.results;
			state.numCrawlerUrls = urls.count;
		}
	},
	actions: {
		async fetchCrawlerHistory( context, page ) {
			let history = [];
			const request1 = { url: '/api/crawler/runs/?page=' + page };

			makeApiCall( context, request1 ).then(
				( success1 ) => {
					history = success1.body;

					const getUrlsForACrawlerRun = async ( cr, index ) => {
						const request2 = { url: '/api/crawler/runs/' + cr.id + '/urls' };

						await makeApiCall( context, request2 ).then(
							( success2 ) => {
								history.results[ index ].urls = success2.body;
								return Promise.resolve( 'ok' );
							},
							( failure ) => {
								return Promise.reject( failure );
							}
						);
					};

					const getCrawlerRuns = async () => {
						await Promise.all( history.results.map( ( cr, index ) => {
							return getUrlsForACrawlerRun( cr, index );
						} ) ).then( () => {
							context.commit( 'CRAWLER_HISTORY', history );
						} ).catch( ( error ) => {
							this._vm.$notify.error( i18n.t( 'apierror', [ error ] ) );
						} );
					};

					getCrawlerRuns();
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
		}
	},
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
