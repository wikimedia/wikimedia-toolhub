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
		const state = {
			apispec: null,
			schemaPromise: null
		};
		const rootState = { locale: { locale: 'en' } };
		const context = { commit, dispatch, state, rootState };

		const apiError = {
			errors: [ {
				field: 'test field1',
				message: 'something went wrong'
			} ]
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

				const promise = actions.fetchOpenAPISchema( context );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit.getCall( 0 ) ).to.have.been.calledWithExactly(
					'SCHEMA_PROMISE', promise
				);

				await promise;

				expect( commit ).to.have.been.calledTwice;
				expect( commit.getCall( 1 ) ).to.have.been.calledWithExactly(
					'onSpecChanged', { spec }
				);

			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				const promise = actions.fetchOpenAPISchema( context );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'SCHEMA_PROMISE', promise
				);

				await promise;
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );

		describe( 'getOperationSchema', () => {
			it( 'should fetch an api operation schema', async () => {
				expect( state.schemaPromise ).to.be.null;

				dispatch.onFirstCall().returns(
					{ then: sinon.stub().yields( spec ) }
				);
				const operation = await actions.getOperationSchema(
					context, 'auditlogs_list'
				);

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledWithExactly(
					'fetchOpenAPISchema'
				);
				expect( operation ).to.equal(
					spec.paths[ '/api/auditlogs/' ].get
				);
			} );

			it( 'should fail on unknown operations', async () => {
				expect( state.schemaPromise ).to.be.null;

				dispatch.onFirstCall().returns(
					{ then: sinon.stub().yields( spec ) }
				);
				let operation;
				try {
					operation = await actions.getOperationSchema(
						context, 'this-does-not-exist'
					);
				} catch ( err ) {
					operation = err;
				}

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledWithExactly(
					'fetchOpenAPISchema'
				);
				expect( operation ).to.be.an.instanceof( Error );
			} );
		} );
	} );

	describe( 'mutations', () => {
		it( 'should store schemaPromise', () => {
			const state = {
				schemaPromise: null
			};
			// eslint-disable-next-line no-unused-vars
			const promise = new Promise( ( resolve, reject ) => {
				resolve( true );
			} );
			mutations.SCHEMA_PROMISE( state, promise );
			expect( state.schemaPromise ).to.equal( promise );
		} );
		it( 'should store apispec', () => {
			const state = {
				apispec: null
			};
			mutations.onSpecChanged( state, { spec } );
			expect( state.apispec ).to.equal( spec );
		} );
	} );

} );
