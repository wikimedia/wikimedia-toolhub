'use strict';
import chai from 'chai';

const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { patternRegexList, patternRegexRule } from './pattern-regex';

describe( 'plugins/pattern-regex', () => {
	describe( 'patternRegexRule', () => {
		patternRegexList.forEach( ( { pattern, description } ) => {
			it( `should expect ${pattern}`, () => {
				const res = patternRegexRule( pattern );
				expect( res ).to.be.an( 'array' ).of.length( 1 );
				expect( res[ 0 ] ).to.be.a( 'function' );
				expect( res[ 0 ]( undefined ) ).to.be.true;
				expect( res[ 0 ]( ' ' ) ).to.equal( description );
			} );
		} );
	} );
} );
