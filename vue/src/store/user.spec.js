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
	} );
} );
