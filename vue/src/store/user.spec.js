'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';
import * as notifications from '@/helpers/notifications';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { actions, mutations } from './user';

describe( 'store/user', () => {
	const testUserObj = {
		is_authenticated: true,
		csrf_token: 'abcd',
		casl: [ {
			action: 'view',
			subject: 'auth/group'
		} ]
	};

	const testUsersObj = {
		count: 2,
		results: [
			{
				id: 2,
				username: 'Srish',
				groups: [
					{
						id: 1,
						name: 'Administrators'
					},
					{
						id: 2,
						name: 'Bureaucrats'
					}
				],
				date_joined: '2021-02-26T20:45:06Z'
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
		const state = { user: { is_authenticated: true } };
		const rootState = {
			locale: { locale: 'en' },
			user: state
		};
		const context = { commit, state, rootState };

		const stubThis = {
			vm: {
				$ability: {
					update: sinon.stub()
				}
			}
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

		describe( 'getUserInfo', () => {

			const response = {
				ok: true,
				status: 200,
				url: '/api/user/',
				headers: {
					'Content-type': 'application/json'
				},
				body: testUserObj
			};

			it( 'should fetch user info', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/user/'
				}, context );
				http.resolves( response );

				const promise = actions.getUserInfo( context, stubThis );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit.getCall( 0 ) ).to.have.been.calledWithExactly(
					'USER_PROMISE', promise
				);

				await promise;

				expect( commit ).to.have.been.calledTwice;
				expect( commit.getCall( 1 ) ).to.have.been.calledWithExactly(
					'USER', response.body
				);

				expect( stubThis.vm.$ability.update )
					.to.have.been.calledWithExactly( testUserObj.casl );
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				const promise = actions.getUserInfo( context, stubThis );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'USER_PROMISE', promise
				);

				await promise;
				expect( displayErrorNotification ).to.have.been.called;
			} );

			it( 'should return existing promise', async () => {
				state.userPromise = new Promise( ( resolve ) => {
					resolve( true );
				} );

				const promise = actions.getUserInfo( context, stubThis );
				const resp = await promise;

				expect( http ).to.have.not.been.called;
				expect( commit ).to.have.not.been.called;
				expect( resp ).to.be.true;
			} );
		} );

		describe( 'listAllUsers', () => {
			const testPayload = {
				page: 1,
				filters: {
					username: 'Srish',
					groups_id: 1
				}
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/users/?page=1&username__contains=Srish&groups__id=1',
				headers: {
					'Content-type': 'application/json'
				},
				body: testUsersObj
			};

			it( 'should fetch users', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/users/?page=1&username__contains=Srish&groups__id=1'
				}, context );
				http.resolves( response );

				await actions.listAllUsers( context, testPayload );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'USERS', testUsersObj
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.listAllUsers( context, testPayload );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'getAuthtoken', () => {
			it( 'should fetch data', async () => {
				const response = {
					ok: true,
					statusCode: 200,
					url: '/api/user/authtoken/',
					headers: {
						'Content-type': 'application/json'
					},
					body: {
						token: '**token**',
						user: {
							id: 1,
							username: 'user'
						}
					}
				};
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/'
				}, context );
				http.resolves( response );

				await actions.getAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'AUTHTOKEN', response.body.token
				);
			} );

			it( 'should store null on 404', async () => {
				const response = {
					ok: false,
					statusCode: 404,
					url: '/api/user/authtoken/',
					headers: {
						'Content-type': 'application/json'
					},
					body: {}
				};
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/'
				}, context );
				http.rejects( response );

				await actions.getAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'AUTHTOKEN', null
				);
			} );

			it( 'should emit error messages', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/'
				}, context );
				http.rejects( apiError );

				await actions.getAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'newAuthtoken', () => {
			it( 'should fetch data', async () => {
				const response = {
					ok: true,
					statusCode: 200,
					url: '/api/user/authtoken/',
					headers: {
						'Content-type': 'application/json'
					},
					body: {
						token: '**token**',
						user: {
							id: 1,
							username: 'user'
						}
					}
				};
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/',
					method: 'POST'
				}, context );
				http.resolves( response );

				await actions.newAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'AUTHTOKEN', response.body.token
				);
			} );

			it( 'should emit error messages', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/',
					method: 'POST'
				}, context );
				http.rejects( apiError );

				await actions.newAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'deleteAuthtoken', () => {
			it( 'should delete', async () => {
				const response = {
					ok: true,
					statusCode: 204,
					url: '/api/user/authtoken/',
					body: {}
				};
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/',
					method: 'DELETE'
				}, context );
				http.resolves( response );

				await actions.deleteAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'AUTHTOKEN', null
				);
			} );

			it( 'should store null on 404', async () => {
				const response = {
					ok: false,
					statusCode: 404,
					url: '/api/user/authtoken/',
					body: {}
				};
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/',
					method: 'DELETE'
				}, context );
				http.rejects( response );

				await actions.deleteAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'AUTHTOKEN', null
				);
			} );

			it( 'should emit error messages', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/',
					method: 'DELETE'
				}, context );
				http.rejects( apiError );

				await actions.deleteAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );
	} );

	describe( 'mutations', () => {

		it( 'should store authtokens', () => {
			const state = {
				authtoken: null
			};

			mutations.AUTHTOKEN( state, '**token**' );
			expect( state.authtoken ).to.equal( '**token**' );

			mutations.AUTHTOKEN( state, null );
			expect( state.authtoken ).to.equal( null );
		} );
	} );
} );
