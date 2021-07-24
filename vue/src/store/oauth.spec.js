'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { asApp, asToken } from '@/helpers/casl';
import { actions, mutations } from './oauth';

describe( 'store/oauth', () => {

	const testClientAppsObj = {
		count: 1,
		results: [
			{
				client_id: 'xyza',
				name: 'test789',
				redirect_url: 'http://test789.co',
				user: {
					id: 2,
					username: 'Srish'
				}
			}
		]
	};

	const testAppObj = testClientAppsObj.results[ 0 ];

	const testAuthorizedAppsObj = {
		count: 1,
		results: [
			{
				id: 2,
				application: testAppObj
			}
		]
	};

	describe( 'actions', () => {
		const commit = sinon.spy();
		const state = { user: { is_authenticated: true } };
		const rootState = {
			locale: { locale: 'en' },
			user: { user: { csrf_token: 'abcd' } }
		};
		const context = { commit, state, rootState };
		const stubThis = {
			_vm: {
				$notify: {
					info: sinon.stub(),
					error: sinon.stub(),
					success: sinon.stub()
				}
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

		describe( 'listClientApps', () => {
			const testPage = 1;
			const response = {
				ok: true,
				status: 200,
				url: '/api/oauth/applications?page=' + testPage,
				headers: { 'Content-type': 'application/json' },
				body: testClientAppsObj
			};

			it( 'should fetch client apps', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/oauth/applications/?page=' + testPage,
					method: 'GET'
				}, context );
				http.resolves( response );
				await actions.listClientApps( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'CLIENT_APPS', testClientAppsObj
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const listClientApps = actions.listClientApps.bind( stubThis );
				await listClientApps( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );
		} );

		describe( 'registerApp', () => {
			const response = {
				ok: true,
				status: 201,
				url: '/api/oauth/applications/',
				headers: { 'Content-type': 'application/json' },
				body: testAppObj
			};

			const app = {
				name: 'test123',
				redirect_url: 'http://test123.com'
			};

			it( 'should register an app', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/oauth/applications/',
					method: 'POST',
					body: JSON.stringify( app )
				}, context );

				http.resolves( response );
				const registerApp = actions.registerApp.bind( stubThis );
				await registerApp( context, app );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'REGISTER_APP', testAppObj
				);
			} );

			it( 'should log failure when error occurs', async () => {
				http.rejects( { errors: [ {
					field: '',
					message: ''
				} ] } );
				const registerApp = actions.registerApp.bind( stubThis );
				await registerApp( context, app );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'REGISTER_APP', false
				);
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );
		} );

		describe( 'deleteClientApp', () => {
			const testClientId = 'jklm';

			const response = {
				ok: true,
				status: 204,
				url: '/api/oauth/applications/' + testClientId + '/',
				headers: { 'Content-length': '0' }
			};

			it( 'should delete a client app', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/oauth/applications/' + testClientId + '/',
					method: 'DELETE'
				}, context );

				http.resolves( response );
				const deleteClientApp = actions.deleteClientApp.bind( stubThis );
				await deleteClientApp( context, testClientId );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly( 'DELETE_CLIENT_APP', testClientId );

			} );

			it( 'should log failure when error occures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const deleteClientApp = actions.deleteClientApp.bind( stubThis );
				await deleteClientApp( context, testClientId );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );
		} );

		describe( 'updateClientApp', () => {
			const app = {
				clientId: testAppObj.clientId,
				redirectUrl: 'http://newurl.com'
			};

			const response = {
				ok: true,
				status: 200,
				headers: { 'Content-type': 'application/json' },
				body: testAppObj
			};

			it( 'should update a client app', async () => {
				http.resolves( response );

				expect( testAppObj.redirect_url ).to.not.equal( app.redirectUrl );
				const updateClientApp = actions.updateClientApp.bind( stubThis );
				await updateClientApp( context, app );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.success ).to.have.been.called;
			} );

			it( 'should log failure when error occures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const updateClientApp = actions.updateClientApp.bind( stubThis );
				await updateClientApp( context, app );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );
		} );

		describe( 'listAuthorizedApps', () => {
			const testPage = 1;
			const response = {
				ok: true,
				status: 200,
				url: '/api/oauth/authorized/?page=' + testPage,
				headers: { 'Content-type': 'application/json' },
				body: testAuthorizedAppsObj
			};

			it( 'should fetch authorized apps', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/oauth/authorized/?page=' + testPage
				}, context );
				http.resolves( response );
				await actions.listAuthorizedApps( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'AUTHORIZED_APPS', testAuthorizedAppsObj
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const listAuthorizedApps = actions.listAuthorizedApps.bind( stubThis );
				await listAuthorizedApps( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );
		} );

		describe( 'deleteAuthorizedApp', () => {
			const testAuthAppId = 'mnop';

			const response = {
				ok: true,
				status: 204,
				url: '/api/oauth/authorized/' + testAuthAppId + '/',
				headers: { 'Content-length': '0' }
			};

			it( 'should delete an authorized app', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/oauth/authorized/' + testAuthAppId + '/',
					method: 'DELETE'
				}, context );

				http.resolves( response );
				const deleteAuthorizedApp = actions.deleteAuthorizedApp.bind( stubThis );
				await deleteAuthorizedApp( context, testAuthAppId );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly( 'DELETE_AUTHORIZED_APP', testAuthAppId );
			} );

			it( 'should log failure when error occures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const deleteAuthorizedApp = actions.deleteAuthorizedApp.bind( stubThis );
				await deleteAuthorizedApp( context, testAuthAppId );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );
		} );

	} );

	describe( 'mutations', () => {
		it( 'should store, register, and delete client apps', () => {
			const state = {
				clientApps: [],
				numClientApps: 0,
				clientAppCreated: {}
			};

			const apps = {
				results: testClientAppsObj.results,
				count: testClientAppsObj.count
			};

			mutations.CLIENT_APPS( state, apps );
			expect( state.clientApps ).to.eql( asApp( apps.results ) );
			expect( state.numClientApps ).to.equal( apps.count );

			mutations.REGISTER_APP( state, testAppObj );
			expect( state.clientApps[ apps.count ] ).to.eql( asApp( testAppObj ) );
			expect( state.numClientApps ).to.equal( apps.count + 1 );

			mutations.DELETE_CLIENT_APP( state, testAppObj.client_id );
			expect( state.clientApps[ apps.count ] ).to.not.eql( asApp( testAppObj ) );
			expect( state.numClientApps ).to.equal( apps.count );
		} );

		it( 'should store and delete authorized apps', () => {
			const state = {
				authorizedApps: [],
				numAuthorizedApps: 0
			};

			const apps = {
				results: testAuthorizedAppsObj.results,
				count: testAuthorizedAppsObj.count
			};

			mutations.AUTHORIZED_APPS( state, apps );
			expect( state.authorizedApps ).to.eql( asToken( apps.results ) );
			expect( state.numAuthorizedApps ).to.equal( apps.count );

			const app = testAuthorizedAppsObj.results[ 0 ];

			mutations.DELETE_AUTHORIZED_APP( state, app.id );
			expect( state.authorizedApps[ apps.count ] ).to.not.eql( asToken( app ) );
			expect( state.numAuthorizedApps ).to.equal( apps.count - 1 );
		} );

	} );
} );
