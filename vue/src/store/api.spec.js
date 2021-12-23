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
} from './api';

const spec = {
	openapi: '3.0.3',
	info: {
		title: 'Toolhub API',
		version: '0.0.1',
		license: [ Object ]
	},
	components: {
		schemas: [ Object ]
	},
	paths: {
		'/api/auditlogs/': {
			get: {
				operationId: 'auditlogs_list',
				description: 'List all log entries.',
				parameters: [ Object ]
			}
		}
	},
	$$normalized: true
};

describe( 'store/api', () => {
	describe( 'actions', () => {
		const commit = sinon.spy();
		const dispatch = sinon.stub();
		const state = { specLoaded: false };
		const rootState = { locale: { locale: 'en' } };
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

		describe( 'fetchOpenAPISchema', () => {
			const response = {
				ok: true,
				status: 200,
				url: '/api/schema/',
				headers: { 'Content-type': 'application/json' },
				body: spec
			};

			it( 'should fetch open api schema', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/schema/'
				}, context );
				http.resolves( response );

				await actions.fetchOpenAPISchema( context );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'onSpecChanged', { spec }
				);
			} );

		} );

		describe( 'getOperationSchema', () => {
			it( 'should fetch an api operation schema', async () => {
				expect( state.specLoaded ).to.equal( false );

				dispatch.onFirstCall().returns( { then: sinon.stub().yields( spec ) } );
				const operation = await actions.getOperationSchema( context, 'auditlogs_list' );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledWithExactly(
					'fetchOpenAPISchema'
				);
				expect( operation ).to.equal( spec.paths[ '/api/auditlogs/' ].get );
			} );
		} );

	} );

	describe( 'mutations', () => {
		it( 'should store `apispec` and `specloaded`', () => {
			const state = {
				apispec: {},
				specLoaded: false
			};

			mutations.onSpecChanged( state, { spec } );
			expect( state.apispec ).to.equal( spec );
			expect( state.specLoaded ).to.equal( true );

		} );
	} );

} );
