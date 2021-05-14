'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';
import i18n from '@/plugins/i18n';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import {
	actions,
	mutations
} from './groups';

describe( 'store/groups', () => {
	const groupsResponse = {
		count: 5,
		results: [ {
			id: 1,
			name: 'Administrators'
		},
		{
			id: 2,
			name: 'Bureaucrats'
		},
		{
			id: 3,
			name: 'Oversighters'
		}
		] };

	const testUsers = [ {
		id: 1,
		username: 'admin',
		groups: [ {
			id: 4,
			name: 'Patrollers'
		} ]
	}
	];

	const groupModifiedResponse = {
		id: 2,
		name: 'Bureaucrats',
		users: testUsers
	};

	describe( 'actions', () => {
		const commit = sinon.spy();
		const state = { user: { is_authenticated: true } };
		const rootState = {
			locale: { locale: 'en' },
			user: {
				user: {
					csrf_token: 'abcd'
				},
				users: testUsers
			}
		};
		const context = { commit, state, rootState };
		const stubThis = {
			_vm: {
				$notify: {
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

		describe( 'listAllUserGroups', () => {
			const testPage = 2;
			const response = {
				ok: true,
				status: 200,
				url: '/api/groups/?page=' + testPage,
				headers: { 'Content-type': 'application/json' },
				body: groupsResponse
			};

			it( 'should fetch groups', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/groups/?page=' + testPage
				}, context );
				http.resolves( response );

				await actions.listAllUserGroups( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'GROUPS', groupsResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const listAllUserGroups = actions.listAllUserGroups.bind( stubThis );
				await listAllUserGroups( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );

		} );

		describe( 'addMemberToGroup', () => {
			const testPayload = {
				group: { id: 2, name: 'Bureaucrats' },
				member: { id: 1, username: 'admin' }
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/groups/' + testPayload.group.id + '/members/' +
                    testPayload.member.id + '/',
				headers: { 'Content-type': 'application/json' },
				body: groupModifiedResponse
			};

			it( 'should add a member to a group', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/groups/' + testPayload.group.id + '/members/' +
                    testPayload.member.id + '/',
					method: 'PUT'
				}, context );

				http.resolves( response );
				await actions.addMemberToGroup( context, testPayload );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledTwice;
				testUsers[ 0 ].groups.push( testPayload.group );

				expect( commit.args ).to.deep.equal( [
					[
						'user/USERS', { results: testUsers, count: testUsers.length },
						{ root: true }
					],
					[
						'NOTIFICATION', { message: i18n.t( 'members-groupadd-success',
							[ testPayload.member.username, testPayload.group.name ] ),
						type: 'success' }
					]
				] );

			} );

			it( 'should log failure when error occures', async () => {
				const error = {
					field: 'add',
					message: 'Cannot add member to the group'
				};
				http.rejects( error );

				await actions.addMemberToGroup( context, testPayload );
				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledOnce;

				expect( commit ).to.have.been.calledWithExactly(
					'NOTIFICATION',
					{
						message: i18n.t( 'apierror', [ error.message ] ),
						type: 'error'
					}
				);
			} );

		} );

		describe( 'removeMemberFromGroup', () => {
			const testPayload = {
				group: { id: 2, name: 'Bureaucrats' },
				member: { id: 1, username: 'admin' }
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/groups/' + testPayload.group.id + '/members/' +
                    testPayload.member.id + '/',
				headers: { 'Content-type': 'application/json' },
				body: groupModifiedResponse
			};

			it( 'should remove a member to a group', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/groups/' + testPayload.group.id + '/members/' +
                    testPayload.member.id + '/',
					method: 'DELETE'
				}, context );

				http.resolves( response );
				await actions.removeMemberFromGroup( context, testPayload );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledTwice;
				testUsers[ 0 ].groups.pop();

				expect( commit.args ).to.deep.equal( [
					[
						'user/USERS', { results: testUsers, count: testUsers.length },
						{ root: true }
					],
					[
						'NOTIFICATION', { message: i18n.t( 'members-groupremove-success',
							[ testPayload.member.username, testPayload.group.name ] ),
						type: 'success' }
					]
				] );
			} );

			it( 'should log failure when error occures', async () => {
				const error = {
					field: 'remove',
					message: 'Cannot remove member to the group'
				};
				http.rejects( error );

				await actions.removeMemberFromGroup( context, testPayload );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledOnce;

				expect( commit ).to.have.been.calledWithExactly(
					'NOTIFICATION',
					{
						message: i18n.t( 'apierror', [ error.message ] ),
						type: 'error'
					}
				);
			} );
		} );

	} );

	describe( 'mutations', () => {
		it( 'should store groups', () => {
			const state = {
				groups: [],
				numGroups: 0,
				nofitication: null
			};

			const groups = {
				results: groupsResponse.results,
				count: groupsResponse.count
			};

			mutations.GROUPS( state, groups );
			expect( state.groups ).to.equal( groups.results );
			expect( state.numGroups ).to.equal( groups.count );
		} );
	} );

} );
