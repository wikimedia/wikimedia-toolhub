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
		id: '568',
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
		id: '598',
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

		describe( 'getNextRevision', () => {
			const id = 91;

			const response = {
				ok: true,
				status: 200,
				url: '/api/recent/' + id + '/next/',
				headers: { 'Content-type': 'application/json' },
				body: change2
			};

			it( 'should get next revision', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/recent/' + id + '/next/'
				}, context );
				http.resolves( response );

				await actions.getNextRevision( context, id );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );

			} );

		} );

		describe( 'undoChangesBetweenRevisions', () => {
			const testchange1 = {
				...change1,
				revId: change1.id
			};

			const testchange2 = {
				...change2,
				revId: change2.id
			};

			const response1 = {
				ok: true,
				status: 200,
				url: '/api/tools/' + testchange1.name + '/revisions/' + testchange1.revId + '/undo/' + testchange2.revId + '/',
				headers: { 'Content-type': 'application/json' },
				body: recentChangesResponse
			};

			const response2 = {
				ok: true,
				status: 200,
				url: '/api/lists/' + testchange2.id + '/revisions/' + testchange2.revId + '/undo/' + testchange1.revId + '/',
				headers: { 'Content-type': 'application/json' },
				body: recentChangesResponse
			};

			const response_next_1 = {
				ok: true,
				status: 200,
				url: '/api/recent/' + testchange1.revId + '/next/',
				headers: { 'Content-type': 'application/json' },
				body: change2
			};

			const response_next_2 = {
				ok: true,
				status: 200,
				url: '/api/recent/' + testchange2.revId + '/next/',
				headers: { 'Content-type': 'application/json' },
				body: change1
			};

			it( 'should undo revision between tools', async () => {

				const expectRequest = addRequestDefaults( {
					url: '/api/tools/' + testchange1.name + '/revisions/' + testchange1.revId + '/undo/' + testchange2.revId + '/',
					method: 'POST'
				}, context );

				dispatch.onFirstCall().returns( { then: sinon.stub().yields( response_next_1 ) } );

				http.resolves( response1 );

				await actions.undoChangesBetweenRevisions( context, testchange1 );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );

			} );

			it( 'should undo revision between lists', async () => {
				dispatch.onFirstCall().returns( { then: sinon.stub().yields( response_next_2 ) } );

				const expectRequest = addRequestDefaults( {
					url: '/api/lists/' + testchange2.id + '/revisions/' + testchange2.revId + '/undo/' + testchange1.revId + '/',
					method: 'POST'
				}, context );

				http.resolves( response2 );

				await actions.undoChangesBetweenRevisions( context, testchange2 );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );

			} );

			it( 'should log failures', async () => {
				dispatch.onFirstCall().returns( { then: sinon.stub().yields( response_next_2 ) } );

				http.rejects( apiError );

				await actions.undoChangesBetweenRevisions( context, testchange1 );

				expect( http ).to.have.been.calledOnce;
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
