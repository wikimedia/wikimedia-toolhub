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
} from './ui';

describe( 'store/ui', () => {
	const homeDataResponse = {
		total_tools: 1493,
		last_crawl_time: '2021-10-04T20:40:00.913796Z',
		last_crawl_changed: 58
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
				http.rejects( { errors: [ {
					field: '',
					message: ''
				} ] } );
				const getHomeData = actions.getHomeData.bind( stubThis );
				await getHomeData( context );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
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
