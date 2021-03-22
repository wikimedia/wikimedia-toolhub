'use strict';
import chai from 'chai';

const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { ensureArray } from './array';

describe( 'utils', () => {
	describe( 'ensureArray', () => {
		it( 'should accept null-like args', () => {
			expect( ensureArray() ).to.be.an( 'array' ).that.is.empty;
			expect( ensureArray( undefined ) ).to.be.an( 'array' )
				.that.is.empty;
			expect( ensureArray( null ) ).to.be.an( 'array' ).that.is.empty;
		} );

		it( 'should pass through array single arg', () => {
			expect( ensureArray( [ 1 ] ) ).to.have.ordered.members( [ 1 ] );
			expect( ensureArray( [ 'foo' ] ) )
				.to.have.ordered.members( [ 'foo' ] );
		} );

		it( 'should create array of args', () => {
			expect( ensureArray( 1 ) ).to.have.ordered.members( [ 1 ] );
			expect( ensureArray( 1, 'foo', [ 0 ] ) )
				.to.have.deep.ordered.members( [ 1, 'foo', [ 0 ] ] );
		} );
	} );
} );
