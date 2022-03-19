'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';
import * as notifications from '@/helpers/notifications';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { asVersion } from '@/helpers/casl';
import {
	actions,
	mutations
} from './recentchanges';

describe( 'store/tools', () => {

	const change1 = {
		comment: 'This is a test edit',
		id: 568,
		parent_id: 567,
		child_id: 569,
		content_type: 'tool',
		content_id: 'this-is-name',
		timestamp: '2021-04-28T20:12:08.025365Z',
		user: {
			id: 2,
			username: 'Srish'
		}
	};

	const change2 = {
		comment: 'This is a test edit!!',
		id: 598,
		parent_id: 597,
		child_id: 599,
		content_type: 'toollist',
		content_id: 1,
		timestamp: '2021-04-27T20:12:08.025365Z',
		user: {
			id: 2,
			username: 'Srish'
		}
	};

	const recentChangesResponse = {
		count: 2,
		results: [
			change1,
			change2
		]
	};

	const apiError = {
		errors: [ {
			field: 'test field1',
			message: 'something went wrong'
		} ]
	};

	describe( 'actions', () => {
		const commit = sinon.spy();
		const dispatch = sinon.stub();
		const state = { user: { is_authenticated: true } };
		const rootState = {
			locale: { locale: 'en' },
			user: { user: { csrf_token: 'abcd' } }
		};
		const context = { commit, dispatch, state, rootState };

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

		describe( 'fetchRecentChanges', () => {

			const response = {
				ok: true,
				status: 200,
				url: '/api/recent/',
				headers: { 'Content-type': 'application/json' },
				body: recentChangesResponse
			};

			it( 'should fetch recent changes', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/recent/?user=Raymond&page=1'
				}, context );
				http.resolves( response );

				await actions.fetchRecentChanges( context, { user: 'Raymond', page: 1 } );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'RECENT_CHANGES', recentChangesResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.fetchRecentChanges( context, {} );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );

	} );

	describe( 'mutations', () => {

		it( 'should store recentchanges', () => {
			const state = {
				recentChanges: [],
				numChanges: 0
			};

			mutations.RECENT_CHANGES( state, recentChangesResponse );
			expect( state.recentChanges ).to.eql( asVersion( recentChangesResponse.results ) );
			expect( state.numChanges ).to.equal( recentChangesResponse.count );

		} );

	} );

} );
