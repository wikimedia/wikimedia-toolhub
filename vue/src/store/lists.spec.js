'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';
import * as notifications from '@/helpers/notifications';
import { asList, asVersion } from '@/helpers/casl';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import {
	actions,
	mutations
} from './lists';

describe( 'store/lists', () => {
	const shortListResponse = {
		title: 'test',
		description: null,
		icon: null,
		tools: [],
		comment: '',
		published: true
	};

	const listResponse = {
		count: 1,
		results: [ {
			...shortListResponse,
			id: 14,
			favorites: false,
			featured: true
		} ]
	};

	const shortListResponseTwo = {
		title: 'my private list',
		description: null,
		icon: null,
		tools: [],
		comment: '',
		published: false
	};

	const listResponseTwo = {
		count: 1,
		results: [ {
			...shortListResponseTwo,
			id: 14,
			favorites: false,
			featured: true
		} ]
	};

	const apiError = {
		errors: [ {
			field: 'test field1',
			message: 'something went wrong'
		} ]
	};

	const listRevisionResponse1 = {
		comment: 'This is a test edit!!',
		id: 596,
		timestamp: '2021-04-27T20:12:08.025365Z',
		user: {
			id: 3,
			username: 'Alice'
		}
	};

	const listRevisionResponse2 = {
		comment: 'This is a test edit!!',
		id: 598,
		timestamp: '2021-04-28T20:12:08.025365Z',
		user: {
			id: 3,
			username: 'Alice'
		}
	};

	const listRevisionsResponse = {
		count: 1,
		results: [
			listRevisionResponse1, listRevisionResponse2
		]
	};

	const diffRevisionResponse = {
		original: {
			id: 593,
			timestamp: '2021-04-28T19:49:31.735437Z',
			user: {
				id: 3,
				username: 'Alice'
			},
			comment: 'Test comment'
		},
		operations: [
			{
				op: 'replace',
				path: '/description',
				value: 'Coolest list ever'
			},
			{
				op: 'replace',
				path: '/title',
				value: 'super-cool-list'
			}
		],
		result: {
			id: 596,
			timestamp: '2021-04-28T20:12:08.025365Z',
			user: {
				id: 3,
				username: 'Alice'
			},
			comment: 'Another test comment'
		}
	};

	describe( 'actions', () => {
		const commit = sinon.spy();
		const dispatch = sinon.stub();
		const state = { user: { is_authenticated: true } };
		const rootState = {
			locale: { locale: 'en' },
			user: { user: { username: 'unit tester', csrf_token: 'abcd' } }
		};
		const context = { commit, dispatch, state, rootState };
		const stubThis = {
			_vm: {
				$notify: {
					success: sinon.stub()
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

		describe( 'getFeaturedLists', () => {
			const testPage = 1;
			const response = {
				ok: true,
				status: 200,
				url: '/api/lists/?featured=true&page=' + testPage,
				headers: { 'Content-type': 'application/json' },
				body: listResponse
			};

			it( 'should fetch featured lists', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/?featured=true&page=' + testPage
				}, context );
				http.resolves( response );

				await actions.getFeaturedLists( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'FEATURED_LISTS', listResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.getFeaturedLists( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'getMyLists', () => {
			const testPage = 1;
			const response = {
				ok: true,
				status: 200,
				url: '/api/lists/?user=unit+tester&page=' + testPage,
				headers: { 'Content-type': 'application/json' },
				body: listResponseTwo
			};

			it( 'should fetch private lists', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/?user=unit+tester&page=' + testPage
				}, context );
				http.resolves( response );

				await actions.getMyLists( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'MY_LISTS', listResponseTwo
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.getMyLists( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'createNewList', () => {
			const response = {
				ok: true,
				status: 201,
				url: '/api/lists/',
				headers: { 'Content-type': 'application/json' },
				body: JSON.stringify( shortListResponse )
			};

			it( 'should create list', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/',
					method: 'POST',
					body: JSON.stringify( shortListResponse )
				}, context );
				http.resolves( response );

				const createNewList = actions.createNewList.bind( stubThis );
				await createNewList( context, shortListResponse );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'CREATE_LIST', JSON.stringify( shortListResponse )
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.createNewList( context, shortListResponse );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'CREATE_LIST', false
				);
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );

		describe( 'editList', () => {
			const testId = 14;
			const response = {
				ok: true,
				status: 201,
				url: '/api/lists/' + testId + '/',
				headers: { 'Content-type': 'application/json' },
				body: JSON.stringify( listResponse )
			};

			it( 'should edit list', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/' + testId + '/',
					method: 'PUT',
					body: JSON.stringify( listResponse.results[ 0 ] )
				}, context );
				http.resolves( response );

				const editList = actions.editList.bind( stubThis );
				await editList( context, listResponse.results[ 0 ] );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.success ).to.have.been.called;
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.editList( context, listResponse.results[ 0 ] );
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );

		describe( 'deleteList', () => {
			const testId = 14;
			const response = {
				ok: true,
				status: 201,
				url: '/api/lists/' + testId + '/',
				headers: { 'Content-type': 'application/json' },
				body: {}
			};

			it( 'should delete list', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/' + testId + '/',
					method: 'DELETE'
				}, context );
				http.resolves( response );

				const deleteList = actions.deleteList.bind( stubThis );
				await deleteList( context, testId );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.success ).to.have.been.called;
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.deleteList( context, testId );
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );

		describe( 'getListById', () => {
			const testId = 14;
			const response = {
				ok: true,
				status: 200,
				url: '/api/lists/' + testId + '/',
				headers: { 'Content-type': 'application/json' },
				body: listResponse
			};

			it( 'should get list info', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/' + testId + '/'
				}, context );
				http.resolves( response );

				await actions.getListById( context, testId );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'LIST', listResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.getListById( context, testId );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );
		describe( 'updateListRevisions', () => {
			const testList = {
				id: 14,
				page: 1
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/lists/' + testList.id + '/revisions/?page=' + testList.page,
				headers: { 'Content-type': 'application/json' },
				body: listRevisionsResponse
			};

			it( 'should fetch and update list revisions', async () => {
				dispatch.onFirstCall().returns( { then: sinon.stub().yields( response ) } );
				actions.updateListRevisions( context, testList );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledBefore( commit );
				expect( dispatch ).to.have.been.calledWithExactly(
					'getRevisions', testList
				);

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'LIST_REVISIONS', listRevisionsResponse
				);
			} );

			it( 'should log failures', async () => {
				dispatch.onFirstCall().rejects( { errors: { error1: { field: 'Boom', message: 'Boom Boom' } } } );

				await actions.updateListRevisions( context, testList );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledBefore( commit );
				expect( dispatch ).to.have.been.calledWithExactly(
					'getRevisions', testList
				);

				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );
		describe( 'getListRevision', () => {
			const testList = {
				id: 14,
				revId: 596
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/',
				headers: { 'Content-type': 'application/json' },
				body: listRevisionResponse1
			};

			it( 'should fetch list revision', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/'
				}, context );
				http.resolves( response );

				await actions.getListRevision( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'LIST_REVISION', listRevisionResponse1
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.getListRevision( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );
		describe( 'getListRevisionsDiff', () => {
			const testList = {
				id: 14,
				revId: 593,
				otherId: 596
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/diff/' + testList.otherId + '/',
				headers: { 'Content-type': 'application/json' },
				body: diffRevisionResponse
			};

			it( 'should fetch diff between revisions', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/diff/' + testList.otherId + '/'
				}, context );
				http.resolves( response );

				await actions.getListRevisionsDiff( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'DIFF_REVISION', diffRevisionResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.getListRevisionsDiff( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );

		describe( 'undoChangesBetweenRevisions', () => {
			const testList = {
				id: 14,
				revId: '596',
				page: 1
			};

			const id = testList.revId,
				listRevisions = listRevisionsResponse.results,
				revIndex = listRevisions.findIndex( ( revision ) => revision.id === id ),
				nextIndex = parseInt( revIndex ) + 1;

			const otherId = listRevisions[ nextIndex ] && listRevisions[ nextIndex ].id;

			const response = {
				ok: true,
				status: 200,
				url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/undo/' + otherId + '/',
				headers: { 'Content-type': 'application/json' },
				body: listResponse
			};

			it( 'should undo between revisions', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/' + testList.id + '/revisions/' + id + '/undo/' + otherId + '/',
					method: 'POST'
				}, context );

				http.resolves( response );

				context.state.listRevisions = listRevisionsResponse.results;
				await actions.undoChangesBetweenRevisions( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( dispatch );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledWithExactly(
					'updateListRevisions', {
						page: testList.page,
						id: testList.id
					}
				);

				context.state.listRevisions = [];
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				context.state.listRevisions = listRevisionsResponse.results;
				await actions.undoChangesBetweenRevisions( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( displayErrorNotification ).to.have.been.called;

				context.state.listRevisions = [];
			} );

		} );

		describe( 'restoreListToRevision', () => {
			const testList = {
				id: 14,
				revId: '596',
				page: 1
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/revert/',
				headers: { 'Content-type': 'application/json' }
			};

			it( 'should restore list to a revision', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/revert/',
					method: 'POST'
				}, context );
				http.resolves( response );

				const restoreListToRevision = actions.restoreListToRevision.bind( stubThis );
				await restoreListToRevision( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledWithExactly(
					'updateListRevisions', {
						page: testList.page,
						id: testList.id
					}
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.restoreListToRevision( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );

		describe( 'hideRevealRevision', () => {
			const testList = {
				id: 14,
				revId: '596',
				page: 1,
				action: 'hide'
			};

			const response = {
				ok: true,
				status: 204,
				url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/' + testList.action + '/',
				headers: { 'Content-type': 'application/json' }
			};

			it( 'should hide a revision', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/' + testList.action + '/',
					method: 'PATCH'
				}, context );
				http.resolves( response );

				const hideRevealRevision = actions.hideRevealRevision.bind( stubThis );
				await hideRevealRevision( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledWithExactly(
					'updateListRevisions', {
						page: testList.page,
						id: testList.id
					}
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.hideRevealRevision( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );

		describe( 'markRevisionAsPatrolled', () => {
			const testList = {
				id: 14,
				revId: '596',
				page: 1
			};

			const response = {
				ok: true,
				status: 204,
				url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/patrol/',
				headers: { 'Content-type': 'application/json' }
			};

			it( 'should patrol a revision', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/lists/' + testList.id + '/revisions/' + testList.revId + '/patrol/',
					method: 'PATCH'
				}, context );
				http.resolves( response );

				const markRevisionAsPatrolled = actions.markRevisionAsPatrolled.bind( stubThis );
				await markRevisionAsPatrolled( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledWithExactly(
					'updateListRevisions', {
						page: testList.page,
						id: testList.id
					}
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.markRevisionAsPatrolled( context, testList );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );

		} );
	} );

	describe( 'mutations', () => {
		it( 'should store featured lists, list, list created', () => {
			const state = {
				featuredLists: [],
				listCreated: {},
				list: {}
			};

			mutations.FEATURED_LISTS( state, listResponse );
			expect( state.featuredLists ).to.eql( asList( listResponse ) );

			mutations.CREATE_LIST( state, shortListResponse );
			expect( state.listCreated ).to.eql( asList( shortListResponse ) );

			mutations.LIST( state, listResponse );
			expect( state.list ).to.eql( asList( listResponse ) );
		} );

		it( 'should store diff and list revisions', () => {
			const state = {
				listRevisions: [],
				numRevisions: 0,
				diffRevision: null,
				listRevision: null
			};

			mutations.LIST_REVISIONS( state, listRevisionsResponse );
			expect( state.listRevisions ).to.eql( asVersion( listRevisionsResponse.results ) );
			expect( state.numRevisions ).to.equal( listRevisionsResponse.count );

			mutations.LIST_REVISION( state, listRevisionResponse1 );
			expect( state.listRevision ).to.eql( asVersion( listRevisionResponse1 ) );

			mutations.DIFF_REVISION( state, diffRevisionResponse );
			expect( state.diffRevision ).to.equal( diffRevisionResponse );
		} );
	} );

} );
