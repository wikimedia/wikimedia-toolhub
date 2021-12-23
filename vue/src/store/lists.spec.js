'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';
import { asList } from '@/helpers/casl';
import * as notifications from '@/helpers/notifications';

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

		describe( 'getListInfo', () => {
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

				await actions.getListInfo( context, testId );

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

				await actions.getListInfo( context, testId );

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
	} );

} );
