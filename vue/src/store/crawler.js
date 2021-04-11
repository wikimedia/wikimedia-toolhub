import Vue from 'vue';
import Vuex from 'vuex';
import SwaggerClient from 'swagger-client';

Vue.use( Vuex );

export default {
	namespaced: true,
	state: {
		crawlerHistory: [],
		crawlerUrls: [],
		lastCrawlerRun: [],
		numCrawlerRuns: 0,
		numCrawlerUrls: 0,
		apiErrorMsg: ''
	},
	mutations: {
		CRAWLER_HISTORY( state, history ) {
			state.crawlerHistory = history.results;
			state.lastCrawlerRun = history.results[ 0 ];
			state.numCrawlerRuns = history.count;
			state.apiErrorMsg = '';
		},
		CRAWLER_URLS( state, urls ) {
			state.crawlerUrls = urls.results;
			state.numCrawlerUrls = urls.count;
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

		async fetchCrawlerHistory( context, page ) {
			let history = [];

			const url1 = '/api/crawler/runs/?page=' + page;
			const response1 = await context.dispatch( 'makeApiCall', url1 );

			if ( response1.error ) {
				context.commit( 'ERROR', response1.error );
				return;
			}

			history = response1.data && response1.data.body;

			const getUrlsForACrawlerRun = async ( cr, index ) => {
				const url2 = '/api/crawler/runs/' + cr.id + '/urls/';
				const response2 = await context.dispatch( 'makeApiCall', url2 );

				if ( response2.error ) {
					return Promise.reject( response2.error );
				}

				history.results[ index ].urls = response2.data.body;
				return Promise.resolve( 'ok' );
			};

			const getCrawlerRuns = async () => {
				await Promise.all( history.results.map( ( cr, index ) => {
					return getUrlsForACrawlerRun( cr, index );
				} ) ).then( () => {
					context.commit( 'CRAWLER_HISTORY', history );
				} ).catch( ( error ) => {
					context.commit( 'ERROR', error );
				} );
			};

			getCrawlerRuns();
		},

		async fetchCrawlerUrls( context, data ) {
			const apiUrl = '/api/crawler/runs/' + data.runId + '/urls/?page=' + data.page;
			const response = await context.dispatch( 'makeApiCall', apiUrl );

			if ( response.error ) {
				context.commit( 'ERROR', response.error );
				return;
			}

			context.commit( 'CRAWLER_URLS', response.data.body );
		}
	},
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
