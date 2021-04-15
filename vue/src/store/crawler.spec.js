'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

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

	describe( 'actions', () => {
		const commit = sinon.spy();
		const state = {};
		const rootState = { locale: { locale: 'en' } };
		const context = { commit, state, rootState };
		const stubThis = {
			_vm: {
				$notify: { error: sinon.stub() }
			}
		};
		let http = 'func';

		beforeEach( () => {
			http = sinon.stub( SwaggerClient, 'http' );
		} );
		afterEach( () => {
			http.restore();
			sinon.reset();
		} );

		describe( 'fetchCrawlerHistory', () => {
			const testPage = 2;
			const response = {
				ok: true,
				status: 200,
				url: '/api/crawler/runs/?page=' + testPage,
				headers: { 'Content-type': 'application/json' },
				body: crawlerHistoryResponse
			};

			it( 'should fetch history', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/crawler/runs/?page=' + testPage
				}, context );
				http.resolves( response );

				await actions.fetchCrawlerHistory( context, testPage );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'CRAWLER_HISTORY', crawlerHistoryResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const fetchCrawlerHistory = actions.fetchCrawlerHistory.bind( stubThis );
				await fetchCrawlerHistory( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );
		} );

		describe( 'fetchCrawlerUrls', () => {
			const testData = {
				runId: 7,
				page: 1
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/crawler/runs/' + testData.runId + '/urls/?page=' + testData.page,
				headers: { 'Content-type': 'application/json' },
				body: crawlerUrlsResponse
			};

			it( 'should fetch urls', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/crawler/runs/' + testData.runId + '/urls/?page=' + testData.page
				}, context );
				http.resolves( response );

				await actions.fetchCrawlerUrls( context, testData );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'CRAWLER_URLS', crawlerUrlsResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const fetchCrawlerUrls = actions.fetchCrawlerUrls.bind( stubThis );
				await fetchCrawlerUrls( context, testData );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
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
	} );

} );
