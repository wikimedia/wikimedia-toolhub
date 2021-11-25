'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { asUrl } from '@/helpers/casl';
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

	const testUrlsObj = {
		count: 1,
		results: [
			{
				id: 1,
				url: 'http://test123.com',
				created_by: {
					id: 2,
					username: 'Srish'
				},
				created_date: '2021-03-01T22:29:50.622642Z'
			}
		]
	};

	const testUrlObj = testUrlsObj.results[ 0 ];

	describe( 'actions', () => {
		const commit = sinon.spy();
		const state = { user: { is_authenticated: true } };
		const rootState = {
			locale: { locale: 'en' },
			user: state
		};
		const context = { commit, state, rootState };
		const stubThis = {
			_vm: {
				$notify: {
					info: sinon.stub(),
					error: sinon.stub(),
					success: sinon.stub()
				}
			},
			vm: {
				$ability: {
					update: sinon.stub()
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
				http.rejects( { response: { data: 'Boom' } } );
				const getUserInfo = actions.getUserInfo.bind( stubThis );
				const promise = getUserInfo( context, stubThis );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'USER_PROMISE', promise
				);

				await promise;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
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
				http.rejects( { response: { data: 'Boom' } } );
				const listAllUsers = actions.listAllUsers.bind( stubThis );
				await listAllUsers( context, testPayload );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );
		} );

		describe( 'getUrlsCreatedByUser', () => {
			const testPage = 1;
			const response = {
				ok: true,
				status: 200,
				url: '/api/crawler/urls/self/?page=' + testPage,
				headers: {
					'Content-type': 'application/json'
				},
				body: testUrlsObj
			};

			it( 'should return when user is not logged in', async () => {
				http.resolves( response );
				context.state.user.is_authenticated = false;
				const getUrlsCreatedByUser = actions.getUrlsCreatedByUser.bind( stubThis );
				await getUrlsCreatedByUser( context, testPage );

				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.info ).to.have.been.called;
				expect( http ).to.not.have.been.called;
				context.state.user.is_authenticated = true;
			} );

			it( 'should fetch urls created by user', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/crawler/urls/self/?page=' + testPage
				}, context );
				http.resolves( response );

				await actions.getUrlsCreatedByUser( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'USER_CREATED_URLS', testUrlsObj
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const getUrlsCreatedByUser = actions.getUrlsCreatedByUser.bind( stubThis );
				await getUrlsCreatedByUser( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
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
				const response = {
					code: 1000,
					message: 'boom!',
					status_code: 500,
					errors: [ {
						code: 1,
						field: 'something',
						message: 'Boom!'
					} ]
				};
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/'
				}, context );
				http.rejects( response );

				const getAuthtoken = actions.getAuthtoken.bind( stubThis );
				await getAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.calledOnce;
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
				const response = {
					code: 1000,
					message: 'boom!',
					status_code: 500,
					errors: [ {
						code: 1,
						field: 'something',
						message: 'Boom!'
					} ]
				};
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/',
					method: 'POST'
				}, context );
				http.rejects( response );

				const newAuthtoken = actions.newAuthtoken.bind( stubThis );
				await newAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.calledOnce;
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
				const response = {
					code: 1000,
					message: 'boom!',
					status_code: 500,
					errors: [ {
						code: 1,
						field: 'something',
						message: 'Boom!'
					} ]
				};
				const expectRequest = addRequestDefaults( {
					url: '/api/user/authtoken/',
					method: 'DELETE'
				}, context );
				http.rejects( response );

				const deleteAuthtoken = actions.deleteAuthtoken.bind( stubThis );
				await deleteAuthtoken( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.calledOnce;
			} );
		} );
	} );

	describe( 'mutations', () => {
		it( 'should store, register, and unregister user created urls', () => {
			const state = {
				userCreatedUrls: [],
				numUserCreatedUrls: 0
			};

			const urls = {
				results: testUrlsObj.results,
				count: testUrlsObj.count
			};

			mutations.USER_CREATED_URLS( state, urls );
			expect( state.userCreatedUrls ).to.eql( asUrl( urls.results ) );
			expect( state.numUserCreatedUrls ).to.equal( urls.count );

			mutations.REGISTER_URL( state, testUrlObj );
			expect( state.userCreatedUrls[ urls.count ] ).to.eql( asUrl( testUrlObj ) );
			expect( state.numUserCreatedUrls ).to.equal( urls.count + 1 );

			mutations.UNREGISTER_URL( state, testUrlObj.url );
			expect( state.userCreatedUrls[ urls.count ] ).to.not.eql( asUrl( testUrlObj ) );
			expect( state.numUserCreatedUrls ).to.equal( urls.count );
		} );

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
