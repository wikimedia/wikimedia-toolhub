'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';
import * as notifications from '@/helpers/notifications';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { actions, mutations } from './favorites';

describe( 'store/favorites', () => {
	const favoritesResponse = {
		count: 1,
		results: [
			{
				name: 'hay-directory',
				title: 'Tools Directory',
				description: 'A way to easily discover Wikimedia-related tools.',
				url: 'http://tools.wmflabs.org/hay/directory',
				keywords: [ 'tools', 'recursion', 'discoverability' ],
				author: 'Hay Kranen',
				icon: null
			}
		]
	};
	const toolResponse = favoritesResponse.results[ 0 ];

	const apiError = {
		errors: [ {
			field: 'test field1',
			message: 'something went wrong'
		} ]
	};

	describe( 'actions', () => {
		// FIXME: can we extract this boilerplate to some shared location
		const commit = sinon.spy();
		const state = { user: { is_authenticated: true } };
		const rootState = {
			locale: { locale: 'en' },
			user: { user: { csrf_token: 'abcd' } }
		};
		const context = { commit, state, rootState };
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

		describe( 'getFavoriteTools', () => {
			const testPage = 1;
			const response = {
				ok: true,
				status: 200,
				url: '/api/user/favorites/?page=' + testPage,
				body: favoritesResponse
			};

			it( 'should fetch users favorite tools', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/user/favorites/?page=' + testPage
				}, context );
				http.resolves( response );

				await actions.getFavoriteTools( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'FAVORITE_TOOLS', favoritesResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.getFavoriteTools( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'addTool', () => {
			const response = {
				ok: true,
				status: 200,
				url: '/api/user/favorites/',
				body: toolResponse
			};

			it( 'should add a tool', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/user/favorites/',
					method: 'POST',
					body: JSON.stringify( { name: toolResponse.name } )
				}, context );
				http.resolves( response );

				await actions.addTool( context, toolResponse.name );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'ADD_FAVORITE', toolResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.addTool( context, 'test-tool' );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'removeTool', () => {
			const response = {
				ok: true,
				status: 204,
				url: '/api/user/favorites/' + toolResponse.name + '/'
			};

			it( 'should remove a tool', async () => {
				const expectRequest = addRequestDefaults( {
					url: response.url,
					method: 'DELETE'
				}, context );
				http.resolves( response );

				await actions.removeTool( context, toolResponse.name );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'REMOVE_FAVORITE', toolResponse.name
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );
				await actions.removeTool( context, 'test-tool' );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'isFavorite', () => {
			const response = {
				ok: true,
				status: 200,
				url: '/api/user/favorites/' + toolResponse.name + '/'
			};
			const response404 = {
				ok: false,
				statusCode: 404,
				url: '/api/user/favorites/' + toolResponse.name + '/'
			};

			it( 'should find a favorite', async () => {
				const expectRequest = addRequestDefaults( {
					url: response.url
				}, context );
				http.resolves( response );

				const resp = await actions.isFavorite( context, toolResponse.name );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.not.have.been.called;
				expect( resp ).to.equal( true );
			} );

			it( 'should return false on 404', async () => {
				const expectRequest = addRequestDefaults( {
					url: response.url
				}, context );
				http.rejects( response404 );

				const resp = await actions.isFavorite( context, toolResponse.name );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.not.have.been.called;
				expect( resp ).to.equal( false );
			} );

			it( 'should log non-404 failures', async () => {
				http.rejects( apiError );
				const resp = await actions.isFavorite( context, 'test-tool' );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
				expect( resp ).to.equal( false );
			} );
		} );
	} );

	describe( 'mutations', () => {
		it( 'should store, add and remove user favorite tools', () => {
			const state = {
				favoriteTools: [],
				numFavoriteTools: 0
			};

			mutations.FAVORITE_TOOLS( state, favoritesResponse );
			expect( state.favoriteTools ).to.eql( favoritesResponse.results );
			expect( state.numFavoriteTools ).to.eql( favoritesResponse.count );
			state.favoriteTools = [];
			state.numFavoriteTools = 0;

			mutations.ADD_FAVORITE( state, toolResponse );
			expect( state.favoriteTools[ 0 ] ).to.eql( toolResponse );
			expect( state.numFavoriteTools ).to.equal( 1 );

			mutations.REMOVE_FAVORITE( state, toolResponse.tool );
			expect( state.favoriteTools[ 0 ] ).to.not.eql( toolResponse );
			expect( state.numFavoriteTools ).to.equal( 0 );
		} );
	} );
} );
