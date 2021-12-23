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
	extractFacets,
	actions,
	mutations
} from './search';

describe( 'store/search', () => {
	const facetResponse = {
		facets: {
			_filter_unittest: {
				doc_count: 42,
				unittest: {
					meta: {
						type: 'type',
						multi: true,
						param: 'unittest__term',
						missing_value: '--',
						missing_param: 'unittest__isnull'
					},
					sum_other_doc_count: 11,
					buckets: [
						{ key: 'muhbukket', doc_count: 11 },
						{ key: 'test', doc_count: 10 },
						{ key: '--', doc_count: 10 }
					]
				}
			}
		}
	};

	const autoCompleteResponse = [ { name: 'tool1', title: 'tool1 title' }, { name: 'tool2', title: 'tool2 title' } ];

	const apiError = {
		errors: [ {
			field: 'test field1',
			message: 'something went wrong'
		} ]
	};

	describe( 'extractFacets', () => {
		it( 'should accept empty filters', () => {
			const filters = [];
			const out = extractFacets( facetResponse, filters );
			expect( out ).to.be.an( 'array' ).with.a.lengthOf( 1 );
			expect( out[ 0 ] ).to.have.all.keys(
				'name', 'type', 'multi', 'param', 'missingValue',
				'missingParam', 'docCount', 'otherCount', 'buckets',
				'selected'
			);
			expect( out[ 0 ].selected ).to.be.an( 'array' ).that.is.empty;
		} );

		it( 'should process a missing filter', () => {
			const filters = [ [ 'unittest__isnull', 1 ] ];
			const out = extractFacets( facetResponse, filters );
			expect( out ).to.be.an( 'array' ).with.lengthOf( 1 );
			expect( out[ 0 ] ).to.have.all.keys(
				'name', 'type', 'multi', 'param', 'missingValue',
				'missingParam', 'docCount', 'otherCount', 'buckets',
				'selected'
			);
			expect( out[ 0 ].selected ).to.be.an( 'array' ).with.lengthOf( 1 );
			expect( out[ 0 ].selected[ 0 ] ).to.equal( '--' );
		} );

		it( 'should process a term filter', () => {
			const filters = [ [ 'unittest__term', 'muhbukket' ] ];
			const out = extractFacets( facetResponse, filters );
			expect( out ).to.be.an( 'array' ).with.a.lengthOf( 1 );
			expect( out[ 0 ] ).to.have.all.keys(
				'name', 'type', 'multi', 'param', 'missingValue',
				'missingParam', 'docCount', 'otherCount', 'buckets',
				'selected'
			);
			expect( out[ 0 ].selected ).to.be.an( 'array' ).with.lengthOf( 1 );
			expect( out[ 0 ].selected[ 0 ] ).to.equal( 'muhbukket' );
		} );

		it( 'should process multiple term filters', () => {
			const filters = [
				[ 'unittest__term', 'muhbukket' ],
				[ 'unittest__term', 'test' ]
			];
			const out = extractFacets( facetResponse, filters );
			expect( out ).to.be.an( 'array' ).with.a.lengthOf( 1 );
			expect( out[ 0 ] ).to.have.all.keys(
				'name', 'type', 'multi', 'param', 'missingValue',
				'missingParam', 'docCount', 'otherCount', 'buckets',
				'selected'
			);
			expect( out[ 0 ].selected ).to.be.an( 'array' ).with.lengthOf( 2 );
			expect( out[ 0 ].selected[ 0 ] ).to.equal( 'muhbukket' );
			expect( out[ 0 ].selected[ 1 ] ).to.equal( 'test' );
		} );
	} );

	describe( 'actions', () => {
		const commit = sinon.spy();
		const state = {};
		const rootState = { locale: { locale: 'en' } };
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

		describe( 'AutoCompleteTools', () => {
			const response = {
				ok: true,
				status: 200,
				url: '/api/autocomplete/tools/',
				headers: { 'Content-type': 'application/json' },
				body: autoCompleteResponse
			};

			it( 'should accept empty payload', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/autocomplete/tools/?'
				}, context );
				http.resolves( response );

				await actions.autoCompleteTools( context, {} );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
			} );

			it( 'should build query string', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/autocomplete/tools/?q=q'
				}, context );
				http.resolves( response );

				await actions.autoCompleteTools( context, {
					query: 'q'
				} );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.autoCompleteTools( context, {} );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledOnce;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );

		describe( 'findTools', () => {
			const response = {
				ok: true,
				status: 200,
				url: '/api/search/tools/',
				headers: { 'Content-type': 'application/json' },
				body: facetResponse
			};

			it( 'should accept empty payload', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/search/tools/?'
				}, context );
				http.resolves( response );

				await actions.findTools( context, {} );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
			} );

			it( 'should build query string', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/search/tools/?q=q&filter=term'
				}, context );
				http.resolves( response );

				await actions.findTools( context, {
					query: 'q',
					filters: [ [ 'filter', 'term' ] ]
				} );
				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );
				expect( commit ).to.have.been.calledOnce;
			} );

			it( 'should log failures', async () => {
				http.rejects( apiError );

				await actions.findTools( context, {} );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				expect( displayErrorNotification ).to.have.been.called;
			} );
		} );
	} );

	describe( 'mutations', () => {
		describe( 'onToolsResults', () => {
			it( 'should store inputs', () => {
				const state = {
					toolsQueryParams: null,
					toolsResponse: {}
				};

				const results = 'whatever';
				const qs = 'something';
				mutations.onToolsResults( state, { results, qs } );

				expect( state.toolsQueryParams ).to.equal( qs );
				expect( state.toolsResponse ).to.equal( results );
			} );
		} );
	} );

} );
