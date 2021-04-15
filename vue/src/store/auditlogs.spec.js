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

	describe( 'actions', () => {
		const commit = sinon.spy();
		const state = {};
		const rootState = { locale: { locale: 'en' } };
		const context = { commit, state, rootState };
		let http = 'func';

		beforeEach( () => {
			http = sinon.stub( SwaggerClient, 'http' );
		} );
		afterEach( () => {
			http.restore();
			sinon.reset();
		} );

		describe( 'fetchAuditLogs', () => {
			const testPage = 2;
			const response = {
				ok: true,
				status: 200,
				url: '/api/auditlogs/?page=' + testPage,
				headers: { 'Content-type': 'application/json' },
				body: auditLogsResponse
			};

			it( 'should fetch logs', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/auditlogs/?page=' + testPage
				}, context );
				http.resolves( response );

				await actions.fetchAuditLogs( context, testPage );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'AUDIT_LOGS', auditLogsResponse
				);
			} );

			it( 'should log failures', async () => {
				const stubThis = {
					_vm: {
						$notify: { error: sinon.stub() }
					}
				};
				http.rejects( { response: { data: 'Boom' } } );
				const fetchAuditLogs = actions.fetchAuditLogs.bind( stubThis );
				await fetchAuditLogs( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
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
