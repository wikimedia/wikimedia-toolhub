'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';
import * as notifications from '@/helpers/notifications';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import {
	actions,
	mutations
} from './ui';

describe( 'store/ui', () => {
	const homeDataResponse = {
		total_tools: 1493,
		last_crawl_time: '2021-10-04T20:40:00.913796Z',
		last_crawl_changed: 58
	};

	const apiError = {
		errors: [ {
			field: 'test field1',
			message: 'something went wrong'
		} ]
	};

	describe( 'actions', () => {
		const commit = sinon.spy();
		const state = {};
		const rootState = { locale: { locale: 'en' } };
		const context = { commit, state, rootState };
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

		describe( 'getHomeData', () => {
			const response = {
				ok: true,
				status: 200,
				url: '/api/ui/home/',
				headers: { 'Content-type': 'application/json' },
				body: homeDataResponse
			};

			it( 'should fetch data', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/ui/home/'
				}, context );
				http.resolves( response );

				await actions.getHomeData( context );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'onHomeData', homeDataResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.getHomeData( context );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );
	} );

	describe( 'mutations', () => {
		it( 'onHomeData', () => {
			const state = {
				totalTools: 0,
				lastCrawlTime: '',
				lastCrawlChanged: 0
			};
			mutations.onHomeData( state, {
				total_tools: 1493,
				last_crawl_time: '2021-10-04T20:40:00.913796Z',
				last_crawl_changed: 58
			} );

			expect( state.totalTools ).to.equal( 1493 );
			expect( state.lastCrawlTime ).to.equal( '2021-10-04T20:40:00.913796Z' );
			expect( state.lastCrawlChanged ).to.equal( 58 );
		} );
	} );

} );
