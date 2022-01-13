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
} from './auditlogs';

describe( 'store/auditlogs', () => {
	const auditLogsResponse = {
		count: 1,
		results: [
			{
				id: 599,
				timestamp: '2021-04-14T02:11:54.977936Z',
				user: {
					id: 2,
					username: 'Bot'
				},
				target: {
					type: 'tool',
					id: 'random',
					label: 'random'
				},
				action: 'updated',
				message: 'test'
			}
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

		describe( 'fetchAuditLogs', () => {
			const testPayload1 = {
				page: 1,
				filters: {
					target_type: 'tool',
					user: 'Bot'
				}
			};

			const testPayload2 = {
				page: 2,
				filters: {
					target_type: null,
					user: 'Bot'
				}
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/auditlogs/?target_type=tool&user=Bot&page=1',
				headers: { 'Content-type': 'application/json' },
				body: auditLogsResponse
			};

			it( 'should fetch logs', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/auditlogs/?target_type=tool&user=Bot&page=1'
				}, context );
				http.resolves( response );

				await actions.fetchAuditLogs( context, testPayload1 );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'AUDIT_LOGS', auditLogsResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.fetchAuditLogs( context, testPayload1 );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );

			it( 'should remove null or undefined filters', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/auditlogs/?user=Bot&page=2'
				}, context );
				http.resolves( response );

				await actions.fetchAuditLogs( context, testPayload2 );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );
			} );
		} );
	} );

	describe( 'mutations', () => {
		it( 'should store logs', () => {
			const state = {
				auditLogs: [],
				numLogs: 0
			};
			const logs = {
				results: auditLogsResponse.results,
				count: auditLogsResponse.count
			};
			mutations.AUDIT_LOGS( state, logs );

			expect( state.auditLogs ).to.equal( logs.results );
			expect( state.numLogs ).to.equal( logs.count );
		} );
	} );

} );
