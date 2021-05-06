'use strict';
import chai from 'chai';

const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { filterEmpty } from './object';

describe( 'helpers/object', () => {
	describe( 'filterEmpty', () => {
		it( 'should accept null-like args', () => {
			expect( filterEmpty() ).to.be.an( 'object' ).that.is.empty;
			expect( filterEmpty( undefined ) ).to.be.an( 'object' )
				.that.is.empty;
			expect( filterEmpty( null ) ).to.be.an( 'object' ).that.is.empty;
		} );

		it( 'should strip null values', () => {
			expect( filterEmpty( { foo: null } ) ).to.be.an( 'object' ).that.is.empty;
			expect( filterEmpty( { foo: null, bar: 1 } ) ).to.eql( { bar: 1 } );
		} );
	} );
} );
