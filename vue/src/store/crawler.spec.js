'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';
import * as notifications from '@/helpers/notifications';
chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { asUrl } from '@/helpers/casl';
import {
	actions,
	mutations
} from './crawler';

describe( 'store/crawler', () => {
	const crawlerHistoryResponse = {
		count: 1,
		results: [
			{
				id: 1,
				start_date: '2021-03-05T01:24:41.816288Z',
				end_date: '2021-03-05T01:25:24.528516Z',
				crawled_urls: 2,
				new_tools: 365,
				updated_tools: 0,
				total_tools: 365
			}
		]
	};

	const crawlerUrlsResponse = {
		count: 1,
		results: [
			{
				id: 7,
				url: 'http://test124.com',
				created_by: {
					id: 2,
					username: 'Srish'
				},
				created_date: '2021-04-23T18:12:42.148717Z'
			}
		]
	};

	const apiError = {
		errors: [ {
			field: 'test field1',
			message: 'something went wrong'
		} ]
	};

	const testUrlObj = crawlerUrlsResponse.results[ 0 ];

	describe( 'actions', () => {
		const commit = sinon.spy();
		const rootState = {
			locale: { locale: 'en' },
			user: { user: { is_authenticated: true, csrf_token: 'abcd' } }
		};
		const context = { commit, rootState };

		const stubThis = {
			_vm: {
				$notify: {
					info: sinon.stub(),
					success: sinon.stub()
				}
			}
		};
		let http = 'func';
		let displayErrorNotification = 'func';

		beforeEach( () => {
			http = sinon.stub( SwaggerClient, 'http' );
			displayErrorNotification = sinon.stub( notifications, 'displayErrorNotification' );
		} );
		afterEach( () => {
			http.restore();
			displayErrorNotification.restore();
			sinon.reset();
		} );

		describe( 'fetchCrawlerHistory', () => {
			const testPayload = {
				page: 2,
				filters: {
					runs_ordering: '-crawled_urls'
				}
			};

			const url = '/api/crawler/runs/?page=2&ordering=-crawled_urls';
			const response = {
				ok: true,
				status: 200,
				url,
				headers: { 'Content-type': 'application/json' },
				body: crawlerHistoryResponse
			};

			it( 'should fetch history', async () => {
				const expectRequest = addRequestDefaults( {
					url
				}, context );
				http.resolves( response );

				await actions.fetchCrawlerHistory( context, testPayload );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'CRAWLER_HISTORY', crawlerHistoryResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.fetchCrawlerHistory( context, testPayload );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'fetchCrawlerUrls', () => {

			const testPayload = {
				page: 1,
				runId: 7,
				filters: {
					urls_ordering: '-url__url'
				}
			};

			const url = '/api/crawler/runs/7/urls/?page=1&ordering=-url__url';

			const response = {
				ok: true,
				status: 200,
				url,
				headers: { 'Content-type': 'application/json' },
				body: crawlerUrlsResponse
			};

			it( 'should fetch urls', async () => {
				const expectRequest = addRequestDefaults( {
					url
				}, context );
				http.resolves( response );

				await actions.fetchCrawlerUrls( context, testPayload );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'CRAWLER_URLS', crawlerUrlsResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.fetchCrawlerUrls( context, testPayload );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'registerUrl', () => {

			const url = '/api/crawler/urls/';

			const response = {
				ok: true,
				status: 201,
				url,
				headers: { 'Content-type': 'application/json' },
				body: JSON.stringify( testUrlObj )
			};

			it( 'should return when user is not logged in', async () => {

				http.resolves( response );
				context.rootState.user.user.is_authenticated = false;

				await actions.registerUrl( context, url );

				expect( http ).to.not.have.been.called;

				context.rootState.user.user.is_authenticated = true;
			} );

			it( 'should log success', async () => {
				http.resolves( response );
				const registerUrl = actions.registerUrl.bind( stubThis );

				await registerUrl( context, url );

				expect( http ).to.have.been.calledOnce;

				expect( commit ).to.have.been.calledOnce;

				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.success ).to.have.been.called;
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.registerUrl( context, url );

				expect( http ).to.have.been.calledOnce;

				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'unregisterUrl', () => {

			const url = '/api/crawler/urls/' + testUrlObj.id + '/';

			const response = {
				ok: true,
				status: 201,
				url,
				headers: { 'Content-type': 'application/json' },
				body: {}
			};

			it( 'should return when user is not logged in', async () => {

				http.resolves( response );
				context.rootState.user.user.is_authenticated = false;

				await actions.unregisterUrl( context, url );

				expect( http ).to.not.have.been.called;

				context.rootState.user.user.is_authenticated = true;
			} );

			it( 'should log success', async () => {
				http.resolves( response );
				const unregisterUrl = actions.unregisterUrl.bind( stubThis );

				await unregisterUrl( context, url );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledOnce;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.success ).to.have.been.called;
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.unregisterUrl( context, url );

				expect( http ).to.have.been.calledOnce;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'getUrlsCreatedByUser', () => {
			const testPayload = {
				page: 1,
				filters: {
					ordering: '-created_date'
				}
			};

			const url = '/api/crawler/urls/self/?page=1&ordering=-created_date';
			const response = {
				ok: true,
				status: 200,
				url,
				headers: {
					'Content-type': 'application/json'
				},
				body: crawlerUrlsResponse
			};

			it( 'should return when user is not logged in', async () => {
				http.resolves( response );
				context.rootState.user.user.is_authenticated = false;
				const getUrlsCreatedByUser = actions.getUrlsCreatedByUser.bind( stubThis );

				await getUrlsCreatedByUser( context, testPayload );

				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.info ).to.have.been.called;
				expect( http ).to.not.have.been.called;
				context.rootState.user.user.is_authenticated = true;
			} );

			it( 'should fetch urls created by user', async () => {
				const expectRequest = addRequestDefaults( { url }, context );
				http.resolves( response );

				await actions.getUrlsCreatedByUser( context, testPayload );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'USER_CREATED_URLS', crawlerUrlsResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.getUrlsCreatedByUser( context, testPayload );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

	} );

	describe( 'mutations', () => {
		it( 'should store crawler history and urls', () => {
			const state = {
				crawlerHistory: [],
				crawlerUrls: [],
				lastCrawlerRun: [],
				numCrawlerRuns: 0,
				numCrawlerUrls: 0
			};

			const history = {
				results: crawlerHistoryResponse.results,
				count: crawlerHistoryResponse.count
			};

			mutations.CRAWLER_HISTORY( state, history );
			expect( state.crawlerHistory ).to.equal( history.results );
			expect( state.numCrawlerRuns ).to.equal( history.count );
			expect( state.lastCrawlerRun ).to.equal( history.results[ 0 ] );

			const urls = {
				results: crawlerUrlsResponse.results,
				count: crawlerUrlsResponse.count
			};

			mutations.CRAWLER_URLS( state, urls );
			expect( state.crawlerUrls ).to.equal( urls.results );
			expect( state.numCrawlerUrls ).to.equal( urls.count );
		} );

		it( 'should store, register, and unregister user created urls', () => {
			const state = {
				userCreatedUrls: [],
				numUserCreatedUrls: 0
			};

			const urls = {
				results: crawlerUrlsResponse.results,
				count: crawlerUrlsResponse.count
			};

			mutations.USER_CREATED_URLS( state, urls );
			expect( state.userCreatedUrls ).to.eql( asUrl( urls.results ) );
			expect( state.numUserCreatedUrls ).to.equal( urls.count );

			mutations.REGISTER_URL( state, testUrlObj );
			expect( state.userCreatedUrls[ urls.count ] ).to.eql( asUrl( testUrlObj ) );
			expect( state.numUserCreatedUrls ).to.equal( urls.count + 1 );

			mutations.UNREGISTER_URL( state, testUrlObj.url );
			expect( state.userCreatedUrls[ urls.count ] ).to.not.eql( asUrl( testUrlObj ) );
			expect( state.numUserCreatedUrls ).to.equal( urls.count );
		} );
	} );

} );
