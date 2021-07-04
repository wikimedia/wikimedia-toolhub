'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import {
	actions,
	mutations
} from './lists';

describe( 'store/lists', () => {
	const listResponse = {
		count: 1,
		results: [ {
			id: 14,
			title: 'test',
			description: null,
			icon: null,
			favorites: false,
			published: true,
			featured: true,
			tools: []
		} ]
	};

	describe( 'actions', () => {
		const commit = sinon.spy();
		const dispatch = sinon.stub();
		const state = {};
		const rootState = {
			locale: { locale: 'en' }
		};
		const context = { commit, dispatch, state, rootState };
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
				// http.rejects( { response: { data: 'Boom' } } );
				http.rejects( { errors: [ {
					field: '',
					message: ''
				} ] } );

				const getFeaturedLists = actions.getFeaturedLists.bind( stubThis );
				await getFeaturedLists( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );
		} );
	} );

	describe( 'mutations', () => {
		it( 'should store featured lists', () => {
			const state = {
				featuredLists: []
			};

			mutations.FEATURED_LISTS( state, listResponse );
			expect( state.featuredLists ).to.eql( listResponse );
		} );

	} );

} );
