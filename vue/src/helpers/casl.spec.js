'use strict';
import chai from 'chai';

const expect = chai.expect;
/* eslint-disable no-unused-expressions */
/* eslint-disable no-underscore-dangle */

import { setPOJOSubjectType } from './casl';

describe( 'helpers/casl', () => {
	describe( 'setPOJOSubjectType', () => {
		it( 'should decorate an object', () => {
			const obj = { key: 'value' };
			const typed = setPOJOSubjectType( 'test/test', obj );
			expect( typed ).to.be.an( 'object' );
			expect( typed.__caslSubjectType__ ).to.exist;
			expect( typed.__caslSubjectType__ ).to.equal( 'test/test' );
		} );

		it( 'should decorate an array of objects', () => {
			const objs = [
				{ key: 'value' },
				{ key: 'eulav' }
			];
			const typed = setPOJOSubjectType( 'test/test', objs );
			expect( typed ).to.be.an( 'array' );
			typed.forEach( ( item ) => {
				expect( item.__caslSubjectType__ ).to.exist;
				expect( item.__caslSubjectType__ ).to.equal( 'test/test' );
			} );
		} );
	} );
} );
