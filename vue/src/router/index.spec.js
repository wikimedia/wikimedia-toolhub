'use strict';
import chai from 'chai';

const expect = chai.expect;

import { scrollBehavior } from './index';

describe( 'router', () => {
	describe( 'scrollBehavior', () => {
		it( 'it should return (0,0) normally', () => {
			expect( scrollBehavior( {}, {} ) ).to.eql( { x: 0, y: 0 } );
		} );
		it( 'it should return savedPosition if provided', () => {
			expect( scrollBehavior( {}, {}, 'saved' ) ).to.eql( 'saved' );
		} );
		it( 'it should return to.hash if provided', () => {
			expect( scrollBehavior( { hash: 'hash' }, {} ) ).to.eql( { selector: 'hash' } );
		} );
	} );
} );
